import sublime, sublime_plugin

class InputStateTracker(sublime_plugin.EventListener):

	def on_query_context(self, view, key, operator, operand, match_all):
		if key == 'direction_down':
			SkipWhitespaceCommand.direction = 'down'
			return True

		if key == 'direction_up':
			SkipWhitespaceCommand.direction = 'up'
			return True

		return None

class SkipWhitespaceCommand(sublime_plugin.TextCommand):

	def get_next_points_for_direction(self, current_points):
		if self.direction == 'down':      
			return (current_points[0] + 1, current_points[1])
		
		if self.direction == 'up':
			return (current_points[0] - 1, current_points[1])

		return None

	def move_to(self, points):
		points = (points[0], 0)
		first_char = ''

		while first_char == '':
			point = self.view.text_point(points[0], points[1])
			first_char = self.view.substr(point).strip()

			if first_char != '':
				break

			points = (points[0], points[1] + 1)

		self.view.sel().clear()
		self.view.sel().add(sublime.Region(point))
		self.view.show(point)

	def get_region_for_point(self, point):
		return self.view.full_line(point)

	def get_total_lines(self):
		line, column = self.view.rowcol(self.view.sel()[0].begin())
		return len(self.view.lines(sublime.Region(0L, self.view.size())))
																										
	def run(self, edit):
		cur_points = next_points = self.view.rowcol(self.view.sel()[0].begin())	
		cur_point = self.view.text_point(cur_points[0], cur_points[1])
		cur_text_length = len(self.view.substr(self.get_region_for_point(cur_point)).strip())

		last_text_length = None
		move = False

		while (move == False):
			next_points = self.get_next_points_for_direction(next_points)
			next_point = self.view.text_point(next_points[0], 0)
			next_text_length = len(self.view.substr(self.get_region_for_point(next_point)).strip())

			if self.direction == 'down' and next_points[0] + 1 == self.get_total_lines():
				break

			if self.direction == 'up' and (next_points[0] == 0 or cur_points[0] == 0):
				if next_points[0] == 0 and next_text_length > 0:
					self.move_to(next_points)
				break

			if self.direction == 'down':
				if next_text_length > 0 and (last_text_length == 0 or cur_text_length == 0):
					self.move_to(next_points)
					move = True				

			if self.direction == 'up':
				if next_text_length == 0 and last_text_length > 0:
					self.move_to(last_points)
					move = True

			last_text_length = next_text_length
			last_points = next_points
