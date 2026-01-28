# -*- coding: utf-8 -*-
# @Module: car
# @Author: YY

def init_app(app):
    """
    初始化模块，注册蓝图

    Args:
        app: Flask应用实例
    """
    # 导入 controller 模块，自动注册所有蓝图
    # 使用 pythonModelName 生成 Python 导入路径
    from ruoyi_car.controller import recommend
    app.register_blueprint(recommend)
    # 使用 pythonModelName 生成 Python 导入路径
    from ruoyi_car.controller import view
    app.register_blueprint(view)
    # 使用 pythonModelName 生成 Python 导入路径
    from ruoyi_car.controller import series
    app.register_blueprint(series)
    # 使用 pythonModelName 生成 Python 导入路径
    from ruoyi_car.controller import sales
    app.register_blueprint(sales)
    # 使用 pythonModelName 生成 Python 导入路径
    from ruoyi_car.controller import model
    app.register_blueprint(model)
    # 使用 pythonModelName 生成 Python 导入路径
    from ruoyi_car.controller import like
    app.register_blueprint(like)
    # 使用 pythonModelName 生成 Python 导入路径
    from ruoyi_car.controller import statistics_info
    app.register_blueprint(statistics_info)
    from ruoyi_car.controller import statistics
    app.register_blueprint(statistics)
