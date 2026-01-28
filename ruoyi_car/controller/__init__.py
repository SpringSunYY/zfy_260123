# -*- coding: utf-8 -*-
# @Module: ruoyi_car/controller

from flask import Blueprint

recommend = Blueprint('recommend', __name__, url_prefix='/car/recommend')
view = Blueprint('view', __name__, url_prefix='/car/view')
series = Blueprint('series', __name__, url_prefix='/car/series')
sales = Blueprint('sales', __name__, url_prefix='/car/sales')
model = Blueprint('model', __name__, url_prefix='/car/model')
like = Blueprint('like', __name__, url_prefix='/car/like')
statistics_info = Blueprint('statistics_info', __name__, url_prefix='/car/statisticsInfo')
statistics=Blueprint('statistics', __name__, url_prefix='/car/statistics')

from . import recommend_controller
from . import view_controller
from . import series_controller
from . import sales_controller
from . import model_controller
from . import like_controller
from . import statistics_info_controller
