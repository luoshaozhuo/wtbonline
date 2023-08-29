# coding: utf-8
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Model(db.Model):
    __tablename__ = 'model'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(255, 'utf8mb4_general_ci'))
    set_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    model = db.Column(db.String(255, 'utf8mb4_general_ci'))
    create_time = db.Column(db.DateTime)
    target = db.Column(db.String(255, 'utf8mb4_general_ci'))



class ModelAnormaly(db.Model):
    __tablename__ = 'model_anormaly'

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer)
    set_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    turbine_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    sample_id = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    probability = db.Column(db.Float)



class ModelLabel(db.Model):
    __tablename__ = 'model_label'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255, 'utf8mb4_general_ci'))
    set_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    turbine_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    sample_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    is_anormaly = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)



class PageSetting(db.Model):
    __tablename__ = 'page_setting'

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(255, 'utf8mb4_general_ci'))
    card = db.Column(db.String(255, 'utf8mb4_general_ci'))
    component_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    property = db.Column(db.String(255, 'utf8mb4_general_ci'))
    value = db.Column(db.String(255, 'utf8mb4_general_ci'))
    order = db.Column(db.String(255, 'utf8mb4_general_ci'))



t_report_configuration = db.Table(
    'report_configuration',
    db.Column('id', db.String(255, 'utf8mb4_general_ci')),
    db.Column('set_id', db.String(255, 'utf8mb4_general_ci')),
    db.Column('chapter', db.String(255, 'utf8mb4_general_ci')),
    db.Column('section', db.String(255, 'utf8mb4_general_ci')),
    db.Column('var_name', db.String(255, 'utf8mb4_general_ci')),
    db.Column('aggrigation', db.String(255, 'utf8mb4_general_ci')),
    db.Column('window_length', db.String(255, 'utf8mb4_general_ci')),
    db.Column('overlap', db.String(255, 'utf8mb4_general_ci'))
)



class ReportScheme(db.Model):
    __tablename__ = 'report_scheme'

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    period = db.Column(db.Float)
    start_time = db.Column(db.DateTime)
    rolling_window = db.Column(db.Float)



class StatisticsAccumulation(db.Model):
    __tablename__ = 'statistics_accumulation'

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    turbine_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    date = db.Column(db.DateTime)
    totalenergy = db.Column(db.Float)
    hourgen = db.Column(db.Float)
    create_time = db.Column(db.DateTime)



class TimedTask(db.Model):
    __tablename__ = 'timed_task'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255, 'utf8mb4_general_ci'))
    status = db.Column(db.String(255, 'utf8mb4_general_ci'))
    type = db.Column(db.String(255, 'utf8mb4_general_ci'))
    period = db.Column(db.Float)
    window = db.Column(db.Float)
    repeat = db.Column(db.Float)
    start_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime)



class TurbineCharacteristicFrequency(db.Model):
    __tablename__ = 'turbine_characteristic_frequency'

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    point_name = db.Column(db.String(255, 'utf8mb4_general_ci'))
    frequency = db.Column(db.Float)



class TurbineModelPoint(db.Model):
    __tablename__ = 'turbine_model_points'

    id = db.Column(db.Integer, primary_key=True)
    select = db.Column(db.Integer)
    stat_opeartion = db.Column(db.Integer)
    stat_sample = db.Column(db.Integer)
    stat_accumlation = db.Column(db.Integer)
    set_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    point_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    point_name = db.Column(db.String(255, 'utf8mb4_general_ci'))
    point_name_en = db.Column(db.String(255, 'utf8mb4_general_ci'))
    var_name = db.Column(db.String(255, 'utf8mb4_general_ci'))
    order_no = db.Column(db.String(255, 'utf8mb4_general_ci'))
    unit = db.Column(db.String(255, 'utf8mb4_general_ci'))
    datatype = db.Column(db.String(255, 'utf8mb4_general_ci'))
    coefficient = db.Column(db.String(255, 'utf8mb4_general_ci'))
    change_save = db.Column(db.String(255, 'utf8mb4_general_ci'))
    local_save = db.Column(db.String(255, 'utf8mb4_general_ci'))
    is_alarm = db.Column(db.String(255, 'utf8mb4_general_ci'))
    max = db.Column(db.String(255, 'utf8mb4_general_ci'))
    min = db.Column(db.String(255, 'utf8mb4_general_ci'))
    default_value = db.Column(db.String(255, 'utf8mb4_general_ci'))
    range_max = db.Column(db.String(255, 'utf8mb4_general_ci'))
    range_min = db.Column(db.String(255, 'utf8mb4_general_ci'))
    plus = db.Column(db.String(255, 'utf8mb4_general_ci'))
    module_blong = db.Column(db.String(255, 'utf8mb4_general_ci'))
    module_order = db.Column(db.String(255, 'utf8mb4_general_ci'))
    addr = db.Column(db.String(255, 'utf8mb4_general_ci'))
    control_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    ems_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    point_type = db.Column(db.String(255, 'utf8mb4_general_ci'))
    open_level = db.Column(db.String(255, 'utf8mb4_general_ci'))
    decdig = db.Column(db.String(255, 'utf8mb4_general_ci'))



class TurbineOperationMode(db.Model):
    __tablename__ = 'turbine_operation_mode'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False)
    descrption = db.Column(db.String(255, 'utf8mb4_general_ci'))



class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50, 'utf8mb4_general_ci'))
    password = db.Column(db.String(255, 'utf8mb4_general_ci'))
    privilege = db.Column(db.Integer)



class WindfarmConfiguration(db.Model):
    __tablename__ = 'windfarm_configuration'

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    turbine_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    map_id = db.Column(db.String(255, 'utf8mb4_general_ci'))
    gearbox_ratio = db.Column(db.Float)
    on_grid_date = db.Column(db.DateTime)
