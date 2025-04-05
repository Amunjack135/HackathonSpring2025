import cv2
import pandas
import math
import typing
import yfinance

import CustomMethodsVI.Math.Plotter as Plotter
import CustomMethodsVI.FileSystem as FileSystem

from CustomMethodsVI.Iterable import minmax
from CustomMethodsVI.Stream import LinqStream


class StockPrice:
	def __init__(self, timestamp: pandas.Timestamp, open_price: float, close_price: float, high: float, low: float):
		self.__timestamp__: pandas.Timestamp = timestamp
		self.__open_price__: float = float(open_price)
		self.__close_price__: float = float(close_price)
		self.__high__: float = float(high)
		self.__low__: float = float(low)

	def __repr__(self) -> str:
		return str(self)

	def __str__(self) -> str:
		return f'<StockPrice: OPEN={self.open}, CLOSE={self.close}, RANGE=[{self.low}, {self.high}]>'

	def to_dict(self) -> dict[str, float]:
		return {
			'TimeStamp': self.timestamp.value,
			'OpenPrice': self.open,
			'ClosePrice': self.close,
			'MomentHigh': self.high,
			'MomentLow': self.low
		}

	@property
	def timestamp(self) -> pandas.Timestamp:
		return self.__timestamp__

	@property
	def open(self) -> float:
		return self.__open_price__

	@property
	def close(self) -> float:
		return self.__close_price__

	@property
	def low(self) -> float:
		return self.__low__

	@property
	def high(self) -> float:
		return self.__high__

	@property
	def range_avg(self) -> float:
		return (self.low + self.high) / 2


class CompanyInfo:
	def __init__(self, company_code: str):
		ticker: yfinance.Ticker = yfinance.Ticker(company_code)
		history: pandas.DataFrame = ticker.history(period='max')
		stockprice: dict[pandas.Timestamp, list[float]] = {}
		history_dict: dict[str, dict[pandas.Timestamp, float]] = history.to_dict()

		for dt, price in history_dict['Open'].items():
			stockprice[dt] = [price]
			assert dt.value is not None

		for dt, price in history_dict['Close'].items():
			stockprice[dt].append(price)
			assert dt.value is not None

		for dt, price in history_dict['High'].items():
			stockprice[dt].append(price)
			assert dt.value is not None

		for dt, price in history_dict['Low'].items():
			stockprice[dt].append(price)
			assert dt.value is not None

		self.__key_order__: tuple[pandas.Timestamp, ...] = tuple(sorted(stockprice.keys(), key=lambda time: time.value))
		self.__stock_prices__: dict[pandas.Timestamp, StockPrice] = {a: StockPrice(a, *b) for a, b in stockprice.items()}
		self.__stock_price_relations__: dict[pandas.Timestamp, float] = {key: (self.__stock_prices__[key].range_avg - self.__stock_prices__[self.__key_order__[i - 1]].range_avg) if i > 0 else 0 for i, key in enumerate(self.__key_order__)}
		self.__income_statement__: pandas.DataFrame = ticker.income_stmt
		self.__balance_sheet__: pandas.DataFrame = ticker.balance_sheet

	def to_dict(self) -> dict[str, typing.Any]:
		return {
			'KeyOrder': tuple(date.value for date in self.__key_order__),
			'StockPrices': {date.value: stock_price.to_dict() for date, stock_price in self.__stock_prices__.items()},
			'StockPriceRelations': {date.value: relation for date, relation in self.__stock_price_relations__.items()},
			'IncomeStatement': {date.value: values for date, values in self.__income_statement__.to_dict().items()},
			'BalanceSheet': {date.value: values for date, values in self.__balance_sheet__.to_dict().items()}
		}

	def get_net_relations(self) -> tuple[float, float, float]:
		net_increase: float = LinqStream(self.__key_order__).select(lambda key: self.__stock_price_relations__[key]).filter(lambda value: value > 0).sum()
		net_decrease: float = LinqStream(self.__key_order__).select(lambda key: self.__stock_price_relations__[key]).filter(lambda value: value < 0).sum()
		combined_net: float = net_increase + net_decrease
		return net_increase, net_decrease, combined_net

	def stock_price_plotter(self) -> Plotter.CartesianScatterPlot2D:
		scatter: Plotter.CartesianScatterPlot2D = Plotter.CartesianScatterPlot2D()
		scatter.new_plot('RANGE_AVG', color=0xFF0000, point_size=1)
		scatter.add_points(*tuple((a.value, (b.low + b.high) / 2) for a, b in self.__stock_prices__.items()))
		#scatter.axis_info('x', lab)
		points = scatter.get_points()
		xmin, xmax = (-10, 10) if len(points) == 0 else minmax(point[0] for point in points)

		eq, _, func = scatter.exponential_regression()
		#scatter.new_plot('EXP', color=0x00FFFF, point_size=1)
		#scatter.axis_info('x', min_=xmin, max_=xmax)
		#scatter.graph(func)

		return scatter

	def stock_price_relation_plotter(self) -> Plotter.CartesianScatterPlot2D:
		scatter: Plotter.CartesianScatterPlot2D = Plotter.CartesianScatterPlot2D()
		scatter.new_plot('REL', color='#0000FF', point_size=1)
		scatter.add_points(*tuple((k.value, self.__stock_price_relations__[k]) for k in self.__key_order__))
		minx, maxx = minmax(point[0] for point in scatter.get_points())
		scatter.active_plot('')
		scatter.plot_info(point_size=1)
		scatter.axis_info('x', min_=minx, max_=maxx)
		scatter.graph(lambda x: 0)
		return scatter

	def income_statement_plotters(self) -> dict[str, Plotter.CartesianScatterPlot2D]:
		date: pandas.Timestamp
		entry: pandas.DataFrame
		plotters: dict[str, Plotter.CartesianScatterPlot2D] = {}

		for row in self.__income_statement__.index:
			scatter: Plotter.CartesianScatterPlot2D = Plotter.CartesianScatterPlot2D()

			for date, entry in self.__income_statement__.items():
				value: float = entry[row]

				if not math.isnan(value):
					scatter.add_points((date.value, value))

			plotters[row] = scatter

		return plotters

	def balance_sheet_plotters(self) -> dict[str, Plotter.CartesianScatterPlot2D]:
		date: pandas.Timestamp
		entry: pandas.DataFrame
		plotters: dict[str, Plotter.CartesianScatterPlot2D] = {}

		for row in self.__balance_sheet__.index:
			scatter: Plotter.CartesianScatterPlot2D = Plotter.CartesianScatterPlot2D()

			for date, entry in self.__balance_sheet__.items():
				value: float = entry[row]

				if not math.isnan(value):
					scatter.add_points((date.value, value))

			plotters[row] = scatter

		return plotters

	def save_stock_prices_csv(self, file_name: str) -> FileSystem.File:
		csv: FileSystem.File = FileSystem.File(file_name)

		with csv.open('w') as f:
			f.write('Nanoseconds Since Epoch,Stock Open Price, Stock Close Price, Stock Low, Stock High\n')
			for date in self.__key_order__:
				stock: StockPrice = self.__stock_prices__[date]
				f.write(f'{date.value},{stock.open},{stock.close},{stock.low},{stock.high}\n')

		return csv

	def save_stock_price_relations_csv(self, file_name: str) -> FileSystem.File:
		csv: FileSystem.File = FileSystem.File(file_name)

		with csv.open('w') as f:
			f.write('Nanoseconds Since Epoch,Momentary Increase\n')
			for date in self.__key_order__:
				f.write(f'{date.value},{self.__stock_price_relations__[date]}\n')

		return csv

	def save_income_statement_csv(self, file_name: str) -> FileSystem.File:
		csv: FileSystem.File = FileSystem.File(file_name)
		date: pandas.Timestamp
		entry: pandas.DataFrame

		with csv.open('w') as f:
			f.write(f'Nanoseconds Since Epoch,{",".join(str(x) for x in self.__income_statement__.index)}\n')
			for date, entry in self.__income_statement__.items():
				f.write(f'{date.value},{",".join(str(entry[col]) for col in self.__income_statement__.index)}\n')

		return csv

	def save_balance_sheet_csv(self, file_name: str) -> FileSystem.File:
		csv: FileSystem.File = FileSystem.File(file_name)
		date: pandas.Timestamp
		entry: pandas.DataFrame

		with csv.open('w') as f:
			f.write(f'Nanoseconds Since Epoch,{",".join(str(x) for x in self.__balance_sheet__.index)}\n')
			for date, entry in self.__balance_sheet__.items():
				f.write(f'{date.value},{",".join(str(entry[col]) for col in self.__balance_sheet__.index)}\n')

		return csv

	def save_csv(self, directory: str) -> FileSystem.Directory:
		base_dir: FileSystem.Directory = FileSystem.Directory(directory)

		if not base_dir.exists():
			base_dir.create()

		self.save_stock_prices_csv(base_dir.file('StockPrices.csv').filepath())
		self.save_stock_price_relations_csv(base_dir.file('StockPriceRelations.csv').filepath())
		self.save_income_statement_csv(base_dir.file('IncomeStatement.csv').filepath())
		self.save_balance_sheet_csv(base_dir.file('BalanceSheet.csv').filepath())
		return base_dir

	def save(self, directory: str) -> FileSystem.Directory:
		base_dir: FileSystem.Directory = FileSystem.Directory(directory)

		if not base_dir.exists():
			base_dir.create()

		self.save_stock_prices_csv(base_dir.file('StockPrices.csv').filepath())
		self.save_stock_price_relations_csv(base_dir.file('StockPriceRelations.csv').filepath())
		self.save_income_statement_csv(base_dir.file('IncomeStatement.csv').filepath())
		self.save_balance_sheet_csv(base_dir.file('BalanceSheet.csv').filepath())

		image_dir: FileSystem.Directory = base_dir.cd('images')

		if not image_dir.exists():
			image_dir.create()

		with image_dir.file('StockPrices.png') as f:
			cv2.imwrite(f.filepath(), self.stock_price_plotter().as_image(show_legend=True))

		with image_dir.file('StockPriceRelations.png') as f:
			cv2.imwrite(f.filepath(), self.stock_price_relation_plotter().as_image(show_legend=True))

		income_dir: FileSystem.Directory = image_dir.cd('IncomeStatement')

		if not income_dir.exists():
			income_dir.create()

		for attribute, plotter in self.income_statement_plotters().items():
			with income_dir.file(f'{attribute}.png') as f:
				cv2.imwrite(f.filepath(), plotter.as_image(show_legend=True))

		balance_dir: FileSystem.Directory = image_dir.cd('BalanceSheet')

		if not balance_dir.exists():
			balance_dir.create()

		for attribute, plotter in self.balance_sheet_plotters().items():
			with balance_dir.file(f'{attribute}.png') as f:
				cv2.imwrite(f.filepath(), plotter.as_image(show_legend=True))

		return base_dir
