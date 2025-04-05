from __future__ import annotations

import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageTk
import numpy
import typing
import tkinter

import CustomMethodsVI.Decorators as Decorators


class AxisPlot2D:
	def __init__(self):
		pass


class Plottable:
	def __init__(self):
		pass

	def show(self) -> None:
		root: tkinter.Tk = tkinter.Tk()
		root.overrideredirect(False)
		root.resizable(False, False)
		root.title(f'{type(self).__name__}@{hex(id(self))}')
		root.configure(background='#222222')

		canvas: tkinter.Canvas = tkinter.Canvas(root, background='#222222', highlightthickness=1, highlightcolor='#eeeeee', highlightbackground='#eeeeee', width=1024, height=1024)
		canvas.pack()

		image: numpy.ndarray[numpy.uint8] = self.as_image()
		pilmage: PIL.Image.Image = PIL.Image.fromarray(image)
		pilmage_tk: PIL.ImageTk.PhotoImage = PIL.ImageTk.PhotoImage(pilmage)
		canvas.create_image(0, 0, image=pilmage_tk, anchor='nw')

		root.mainloop()

	def save(self, filename: str) -> None:
		image: PIL.Image.Image = PIL.Image.fromarray(self.as_image())
		image.save(filename)

	def as_image(self) -> numpy.ndarray[numpy.uint8]:
		image: PIL.Image.Image = PIL.Image.new('RGBA', (1024, 1024), '#222222')
		return numpy.array(image)

class Plot2D(Plottable):
	def __init__(self):
		super().__init__()
		self.__points__: set[tuple[float, float]] = set()
		self.__point_shape__: str = 'square'
		self.__point_color__: int = 0xFFFFFF
		self.__point_size__: int = 10

	@Decorators.Overload
	def plot_info(self, *, point_shape: typing.Optional[str] = ..., point_color: typing.Optional[str | int | tuple[int, int, int]] = ..., point_size: typing.Optional[int] = ...) -> None:
		self.__point_shape__ = self.__point_shape__ if point_shape is None or point_shape is ... else str(point_shape)
		self.__point_size__ = self.__point_size__ if point_size is None or point_size is ... else max(0, int(point_size))

		if point_color is ... or point_color is None:
			return
		elif isinstance(point_color, str):
			self.__point_color__ = int(point_color[1:], 16) & 0xFFFFFF
		elif isinstance(point_color, int):
			self.__point_color__ =  int(point_color) & 0xFFFFFF
		elif isinstance(point_color, tuple) and len(point_color) == 3:
			self.__point_color__ = point_color[0] | (point_color[1] >> 8) | (point_color[2] >> 16)
		else:
			raise ValueError(f'Invalid point color - \'{point_color}\'')

	def add_points(self, *points: tuple[float, float] | list[float]) -> None:
		for point in points:
			if not isinstance(point, (tuple, list)) or len(point) != 2 or not all(isinstance(x, (int, float)) for x in point):
				raise ValueError(f'Invalid point - \'{point}\'')

		self.__points__.update(points)


class MultiPlot2D(Plottable):
	def __init__(self):
		super().__init__()
		self.__plots__: dict[str, Plot2D] = {'': Plot2D()}
		self.__plot_order__: list[str] = ['']
		self.__active_plot__: str = ''

	def __getitem__(self, index: int) -> Plot2D:
		index = index if index > 0 else (len(self.__plot_order__) + index)

		if index >= len(self.__plot_order__):
			raise IndexError(f'Index {index} out of bounds for multi-plot with {len(self.__plot_order__)} plots')

		return self.__plots__[self.__plot_order__[index]]


class CartesianScatterPlot2D(MultiPlot2D, AxisPlot2D):
	pass