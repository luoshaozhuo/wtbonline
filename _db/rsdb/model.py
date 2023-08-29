# coding: utf-8
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class AppConfiguration(db.Model):
    __tablename__ = 'app_configuration'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255, 'utf8mb4_general_ci'))
    value = db.Column(db.String(255, 'utf8mb4_general_ci'))



class AppServer(db.Model):
    __tablename__ = 'app_server'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20, 'utf8mb4_general_ci'))
    host = db.Column(db.String(20, 'utf8mb4_general_ci'))
    remote = db.Column(db.Integer)
    type = db.Column(db.String(20, 'utf8mb4_general_ci'))
    port = db.Column(db.Integer)
    user = db.Column(db.String(255, 'utf8mb4_general_ci'))
    password = db.Column(db.String(255, 'utf8mb4_general_ci'))
    database = db.Column(db.String(20, 'utf8mb4_general_ci'))



class Model(db.Model):
    __tablename__ = 'model'
    __table_args__ = (
        db.ForeignKeyConstraint(['set_id', 'turbine_id'], ['windfarm_configuration.set_id', 'windfarm_configuration.turbine_id'], ondelete='RESTRICT', onupdate='CASCADE'),
        db.Index('compoud', 'set_id', 'turbine_id', 'name', 'create_time')
    )

    id = db.Column(db.Integer, primary_key=True)
    farm_name = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, info='与tdengine里的set_id对应')
    turbine_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True, info='与tdengine里的sdevice对应')
    uuid = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, unique=True, info='模型唯一码')
    name = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, info='模型类型')
    start_time = db.Column(db.DateTime, nullable=False, info='建模数据起始时间')
    end_time = db.Column(db.DateTime, nullable=False, info='建模数据结束时间')
    is_local = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1=利用本地数据训练得到的模型')
    create_time = db.Column(db.DateTime, nullable=False, info='本记录生成时间')

    set = db.relationship('WindfarmConfiguration', primaryjoin='and_(Model.set_id == WindfarmConfiguration.set_id, Model.turbine_id == WindfarmConfiguration.turbine_id)', backref='models')



class ModelAnormaly(db.Model):
    __tablename__ = 'model_anormaly'
    __table_args__ = (
        db.ForeignKeyConstraint(['set_id', 'turbine_id'], ['windfarm_configuration.set_id', 'windfarm_configuration.turbine_id'], ondelete='RESTRICT', onupdate='CASCADE'),
        db.Index('set_id_2', 'set_id', 'turbine_id')
    )

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True)
    turbine_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True)
    sample_id = db.Column(db.Integer, nullable=False, index=True)
    bin = db.Column(db.DateTime, nullable=False)
    model_uuid = db.Column(db.String(100, 'utf8mb4_general_ci'), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)

    set = db.relationship('WindfarmConfiguration', primaryjoin='and_(ModelAnormaly.set_id == WindfarmConfiguration.set_id, ModelAnormaly.turbine_id == WindfarmConfiguration.turbine_id)', backref='model_anormalies')



class ModelLabel(db.Model):
    __tablename__ = 'model_label'
    __table_args__ = (
        db.ForeignKeyConstraint(['set_id', 'turbine_id'], ['windfarm_configuration.set_id', 'windfarm_configuration.turbine_id'], ondelete='RESTRICT', onupdate='CASCADE'),
        db.Index('set_id_3', 'set_id', 'turbine_id')
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.ForeignKey('user.username', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, index=True)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False)
    turbine_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True)
    sample_id = db.Column(db.Integer, nullable=False, index=True)
    bin = db.Column(db.DateTime, nullable=False)
    is_anormaly = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)

    set = db.relationship('WindfarmConfiguration', primaryjoin='and_(ModelLabel.set_id == WindfarmConfiguration.set_id, ModelLabel.turbine_id == WindfarmConfiguration.turbine_id)', backref='model_labels')
    user = db.relationship('User', primaryjoin='ModelLabel.username == User.username', backref='model_labels')



class StatisticsSample(db.Model):
    __tablename__ = 'statistics_sample'
    __table_args__ = (
        db.Index('a', 'set_id', 'turbine_id', 'bin', 'create_time'),
    )

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False)
    turbine_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True)
    bin = db.Column(db.DateTime, nullable=False, index=True)
    var_101_mean = db.Column(db.Float)
    var_101_rms = db.Column(db.Float)
    var_101_iqr = db.Column(db.Float)
    var_101_std = db.Column(db.Float)
    var_101_skew = db.Column(db.Float)
    var_101_kurt = db.Column(db.Float)
    var_101_wf = db.Column(db.Float)
    var_101_crest = db.Column(db.Float)
    var_101_zc = db.Column(db.Float)
    var_101_cv = db.Column(db.Float)
    var_102_mean = db.Column(db.Float)
    var_102_rms = db.Column(db.Float)
    var_102_iqr = db.Column(db.Float)
    var_102_std = db.Column(db.Float)
    var_102_skew = db.Column(db.Float)
    var_102_kurt = db.Column(db.Float)
    var_102_wf = db.Column(db.Float)
    var_102_crest = db.Column(db.Float)
    var_102_zc = db.Column(db.Float)
    var_102_cv = db.Column(db.Float)
    var_103_mean = db.Column(db.Float)
    var_103_rms = db.Column(db.Float)
    var_103_iqr = db.Column(db.Float)
    var_103_std = db.Column(db.Float)
    var_103_skew = db.Column(db.Float)
    var_103_kurt = db.Column(db.Float)
    var_103_wf = db.Column(db.Float)
    var_103_crest = db.Column(db.Float)
    var_103_zc = db.Column(db.Float)
    var_103_cv = db.Column(db.Float)
    var_226_mean = db.Column(db.Float)
    var_226_rms = db.Column(db.Float)
    var_226_iqr = db.Column(db.Float)
    var_226_std = db.Column(db.Float)
    var_226_skew = db.Column(db.Float)
    var_226_kurt = db.Column(db.Float)
    var_226_wf = db.Column(db.Float)
    var_226_crest = db.Column(db.Float)
    var_226_zc = db.Column(db.Float)
    var_226_cv = db.Column(db.Float)
    var_246_mean = db.Column(db.Float)
    var_246_rms = db.Column(db.Float)
    var_246_iqr = db.Column(db.Float)
    var_246_std = db.Column(db.Float)
    var_246_skew = db.Column(db.Float)
    var_246_kurt = db.Column(db.Float)
    var_246_wf = db.Column(db.Float)
    var_246_crest = db.Column(db.Float)
    var_246_zc = db.Column(db.Float)
    var_246_cv = db.Column(db.Float)
    var_2709_mean = db.Column(db.Float)
    var_2709_rms = db.Column(db.Float)
    var_2709_iqr = db.Column(db.Float)
    var_2709_std = db.Column(db.Float)
    var_2709_skew = db.Column(db.Float)
    var_2709_kurt = db.Column(db.Float)
    var_2709_wf = db.Column(db.Float)
    var_2709_crest = db.Column(db.Float)
    var_2709_zc = db.Column(db.Float)
    var_2709_cv = db.Column(db.Float)
    var_355_mean = db.Column(db.Float)
    var_355_rms = db.Column(db.Float)
    var_355_iqr = db.Column(db.Float)
    var_355_std = db.Column(db.Float)
    var_355_skew = db.Column(db.Float)
    var_355_kurt = db.Column(db.Float)
    var_355_wf = db.Column(db.Float)
    var_355_crest = db.Column(db.Float)
    var_355_zc = db.Column(db.Float)
    var_355_cv = db.Column(db.Float)
    var_356_mean = db.Column(db.Float)
    var_356_rms = db.Column(db.Float)
    var_356_iqr = db.Column(db.Float)
    var_356_std = db.Column(db.Float)
    var_356_skew = db.Column(db.Float)
    var_356_kurt = db.Column(db.Float)
    var_356_wf = db.Column(db.Float)
    var_356_crest = db.Column(db.Float)
    var_356_zc = db.Column(db.Float)
    var_356_cv = db.Column(db.Float)
    evntemp_mean = db.Column(db.Float)
    evntemp_rms = db.Column(db.Float)
    evntemp_iqr = db.Column(db.Float)
    evntemp_std = db.Column(db.Float)
    evntemp_skew = db.Column(db.Float)
    evntemp_kurt = db.Column(db.Float)
    evntemp_wf = db.Column(db.Float)
    evntemp_crest = db.Column(db.Float)
    evntemp_zc = db.Column(db.Float)
    evntemp_cv = db.Column(db.Float)
    var_372_mean = db.Column(db.Float)
    var_372_rms = db.Column(db.Float)
    var_372_iqr = db.Column(db.Float)
    var_372_std = db.Column(db.Float)
    var_372_skew = db.Column(db.Float)
    var_372_kurt = db.Column(db.Float)
    var_372_wf = db.Column(db.Float)
    var_372_crest = db.Column(db.Float)
    var_372_zc = db.Column(db.Float)
    var_372_cv = db.Column(db.Float)
    var_382_mean = db.Column(db.Float)
    var_382_rms = db.Column(db.Float)
    var_382_iqr = db.Column(db.Float)
    var_382_std = db.Column(db.Float)
    var_382_skew = db.Column(db.Float)
    var_382_kurt = db.Column(db.Float)
    var_382_wf = db.Column(db.Float)
    var_382_crest = db.Column(db.Float)
    var_382_zc = db.Column(db.Float)
    var_382_cv = db.Column(db.Float)
    var_383_mean = db.Column(db.Float)
    var_383_rms = db.Column(db.Float)
    var_383_iqr = db.Column(db.Float)
    var_383_std = db.Column(db.Float)
    var_383_skew = db.Column(db.Float)
    var_383_kurt = db.Column(db.Float)
    var_383_wf = db.Column(db.Float)
    var_383_crest = db.Column(db.Float)
    var_383_zc = db.Column(db.Float)
    var_383_cv = db.Column(db.Float)
    var_409_mean = db.Column(db.Float)
    var_409_rms = db.Column(db.Float)
    var_409_iqr = db.Column(db.Float)
    var_409_std = db.Column(db.Float)
    var_409_skew = db.Column(db.Float)
    var_409_kurt = db.Column(db.Float)
    var_409_wf = db.Column(db.Float)
    var_409_crest = db.Column(db.Float)
    var_409_zc = db.Column(db.Float)
    var_409_cv = db.Column(db.Float)
    var_94_mean = db.Column(db.Float)
    var_94_rms = db.Column(db.Float)
    var_94_iqr = db.Column(db.Float)
    var_94_std = db.Column(db.Float)
    var_94_skew = db.Column(db.Float)
    var_94_kurt = db.Column(db.Float)
    var_94_wf = db.Column(db.Float)
    var_94_crest = db.Column(db.Float)
    var_94_zc = db.Column(db.Float)
    var_94_cv = db.Column(db.Float)
    ongrid_mode = db.Column(db.String(20, 'utf8mb4_general_ci'))
    ongrid_unique = db.Column(db.String(50, 'utf8mb4_general_ci'))
    ongrid_nunique = db.Column(db.Integer)
    limitpowbool_mode = db.Column(db.String(10, 'utf8mb4_general_ci'))
    limitpowbool_unique = db.Column(db.String(20, 'utf8mb4_general_ci'))
    limitpowbool_nunique = db.Column(db.Integer)
    workmode_mode = db.Column(db.String(20, 'utf8mb4_general_ci'))
    workmode_unique = db.Column(db.String(50, 'utf8mb4_general_ci'))
    workmode_nunique = db.Column(db.Integer)
    totalfaultbool_mode = db.Column(db.String(10, 'utf8mb4_general_ci'))
    totalfaultbool_unique = db.Column(db.String(20, 'utf8mb4_general_ci'))
    totalfaultbool_nunique = db.Column(db.Integer)
    nobs = db.Column(db.Float)
    validation = db.Column(db.Float)
    pv_c = db.Column(db.Float)
    pv_t = db.Column(db.Float)
    pv_ctt = db.Column(db.Float)
    create_time = db.Column(db.DateTime, nullable=False)



class TimedTaskLog(db.Model):
    __tablename__ = 'timed_task_log'

    id = db.Column(db.Integer, primary_key=True)
    success = db.Column(db.Integer, nullable=False)
    func = db.Column(db.String(40, 'utf8mb4_general_ci'), nullable=False)
    args = db.Column(db.String(255, 'utf8mb4_general_ci'))
    kwargs = db.Column(db.String(255, 'utf8mb4_general_ci'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    pid = db.Column(db.Integer, nullable=False)



class TurbineModelPoint(db.Model):
    __tablename__ = 'turbine_model_points'

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.ForeignKey('windfarm_infomation.set_id', ondelete='RESTRICT', onupdate='CASCADE'), index=True)
    select = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1=采集到本地tdengine')
    stat_operation = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1=用于计算statistics_operation表的字段')
    stat_sample = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1=用于计算statistics_sample表的字段')
    stat_accumulation = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1=用于计算statistics_accumluation表的字段')
    point_name = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False)
    var_name = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False, info='本地tdengine，set_id=20835的var_name，不变量')
    datatype = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False)
    unit = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False)
    ref_name = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False, info='远程tdengine的变量名，按需修改')

    set = db.relationship('WindfarmInfomation', primaryjoin='TurbineModelPoint.set_id == WindfarmInfomation.set_id', backref='turbine_model_points')



class TurbineOperationMode(db.Model):
    __tablename__ = 'turbine_operation_mode'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False)
    descrption = db.Column(db.String(255, 'utf8mb4_general_ci'))



class TurbineVariableBound(db.Model):
    __tablename__ = 'turbine_variable_bound'

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.ForeignKey('windfarm_infomation.set_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, index=True, server_default=db.FetchedValue(), info='model_point对应字段')
    var_name = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, unique=True, info='model_point对应字段')
    name = db.Column(db.String(20, 'utf8mb4_general_ci'), info='需要显示的中文名称')
    lower_bound = db.Column(db.Float, nullable=False, server_default=db.FetchedValue(), info='报警下限，单位与model_point一致')
    upper_bound = db.Column(db.Float, nullable=False, server_default=db.FetchedValue(), info='报警上限，单位与model_point一致')

    set = db.relationship('WindfarmInfomation', primaryjoin='TurbineVariableBound.set_id == WindfarmInfomation.set_id', backref='turbine_variable_bounds')



class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, index=True, info='用户名')
    password = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False, info='密码')
    privilege = db.Column(db.Integer, nullable=False, info='权限，1-具备账号管理功能，2-普通账户')



class WindfarmConfiguration(db.Model):
    __tablename__ = 'windfarm_configuration'
    __table_args__ = (
        db.ForeignKeyConstraint(['set_id', 'model_name'], ['windfarm_turbine_model.set_id', 'windfarm_turbine_model.model_name'], ondelete='RESTRICT', onupdate='CASCADE'),
        db.Index('windfarm_configuration_ibfk_1', 'set_id', 'model_name'),
        db.Index('set_id_2', 'set_id', 'turbine_id')
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True, info='与tdengine里的set_id对应')
    turbine_id = db.Column(db.String(20, 'utf8mb4_general_ci'), primary_key=True, nullable=False, index=True, info='与tdengine里的device对应')
    map_id = db.Column(db.String(20, 'utf8mb4_general_ci'), primary_key=True, nullable=False, info='现场使用的设备编号')
    model_name = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, info='windfarm_turbine_model键值')
    gearbox_ratio = db.Column(db.Float, nullable=False, info='齿轮箱速比')
    on_grid_date = db.Column(db.DateTime, info='并网日期')

    set = db.relationship('WindfarmTurbineModel', primaryjoin='and_(WindfarmConfiguration.set_id == WindfarmTurbineModel.set_id, WindfarmConfiguration.model_name == WindfarmTurbineModel.model_name)', backref='windfarm_configurations')



class WindfarmInfomation(db.Model):
    __tablename__ = 'windfarm_infomation'

    id = db.Column(db.Integer, primary_key=True)
    farm_name = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, info='风场名')
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True, server_default=db.FetchedValue(), info='对应tdengine里的set_id')



class WindfarmPowerCurve(db.Model):
    __tablename__ = 'windfarm_power_curve'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.ForeignKey('windfarm_turbine_model.model_name', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, index=True)
    mean_speed = db.Column(db.Float, nullable=False)
    mean_power = db.Column(db.Float, nullable=False)

    windfarm_turbine_model = db.relationship('WindfarmTurbineModel', primaryjoin='WindfarmPowerCurve.model_name == WindfarmTurbineModel.model_name', backref='windfarm_power_curves')



class WindfarmTurbineModel(db.Model):
    __tablename__ = 'windfarm_turbine_model'
    __table_args__ = (
        db.Index('set_id', 'set_id', 'model_name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.ForeignKey('windfarm_infomation.set_id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, server_default=db.FetchedValue())
    model_name = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False, index=True, info='配置名')
    rated_power = db.Column(db.VARBINARY(20), nullable=False, info='额定功率')
    blade = db.Column(db.String(255, 'utf8mb4_general_ci'), info='叶片型号')
    gearbox = db.Column(db.String(255, 'utf8mb4_general_ci'), info='齿轮箱型号')
    generator = db.Column(db.String(255, 'utf8mb4_general_ci'), info='发电机型号')
    convertor = db.Column(db.String(255, 'utf8mb4_general_ci'), info='变流器型号')

    set = db.relationship('WindfarmInfomation', primaryjoin='WindfarmTurbineModel.set_id == WindfarmInfomation.set_id', backref='windfarm_turbine_models')
