# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()



class AppConfiguration(db.Model):
    __tablename__ = 'app_configuration'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255, 'utf8mb4_general_ci'), info='键值')
    value = db.Column(db.String(255, 'utf8mb4_general_ci'), info='实际值')
    comment = db.Column(db.String(255, 'utf8mb4_general_ci'), info='说明')



class AppServer(db.Model):
    __tablename__ = 'app_server'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20, 'utf8mb4_general_ci'), info='服务器名')
    host = db.Column(db.String(20, 'utf8mb4_general_ci'), info='地址')
    version = db.Column(db.String(20, 'utf8mb4_general_ci'), info='数据库引擎版本')
    remote = db.Column(db.Integer, info='是否远程服务器')
    type = db.Column(db.String(20, 'utf8mb4_general_ci'), info='用retapi还是cli接口')
    port = db.Column(db.Integer, info='端口')
    user = db.Column(db.String(255, 'utf8mb4_general_ci'), info='用户名')
    password = db.Column(db.String(255, 'utf8mb4_general_ci'), info='密码')
    database = db.Column(db.String(20, 'utf8mb4_general_ci'), info='库名')



class ApschedulerJob(db.Model):
    __tablename__ = 'apscheduler_jobs'

    id = db.Column(db.String(191, 'utf8mb4_general_ci'), primary_key=True)
    next_run_time = db.Column(db.Double(asdecimal=True), index=True)
    job_state = db.Column(db.LargeBinary, nullable=False)



class Model(db.Model):
    __tablename__ = 'model'
    __table_args__ = (
        db.Index('compoud', 'set_id', 'device_id', 'create_time'),
    )

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, info='与tdengine里的set_id对应')
    device_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True, info='与tdengine里的device对应')
    type = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, info='模型类型，如anomaly')
    uuid = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, unique=True, info='模型唯一码')
    start_time = db.Column(db.DateTime, nullable=False, info='建模数据起始时间')
    end_time = db.Column(db.DateTime, nullable=False, info='建模数据结束时间')
    create_time = db.Column(db.DateTime, nullable=False, info='本记录生成时间')



class ModelAnomaly(db.Model):
    __tablename__ = 'model_anomaly'
    __table_args__ = (
        db.Index('set_id_2', 'set_id', 'device_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True)
    device_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True)
    sample_id = db.Column(db.Integer, nullable=False, index=True, info='statistics_sample的记录ID')
    bin = db.Column(db.DateTime, nullable=False, info='样本开始时间')
    model_uuid = db.Column(db.String(100, 'utf8mb4_general_ci'), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)



class ModelLabel(db.Model):
    __tablename__ = 'model_label'
    __table_args__ = (
        db.Index('set_id_3', 'set_id', 'device_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.ForeignKey('user.username', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, index=True, info='用户名')
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False)
    device_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True)
    sample_id = db.Column(db.Integer, nullable=False, index=True, info='statistics_sample的id')
    is_anomaly = db.Column(db.Integer, nullable=False, info='是否异常值')
    create_time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', primaryjoin='ModelLabel.username == User.username', backref='model_labels')



class StatisticsFault(db.Model):
    __tablename__ = 'statistics_fault'
    __table_args__ = (
        db.Index('set_id', 'set_id', 'device_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False)
    device_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False)
    fault_id = db.Column(db.Integer, nullable=False, info='turbine_fault_type的id值')
    value = db.Column(db.String(30, 'utf8mb4_general_ci'), nullable=False, info='flag/fault/alarm/msg 的值')
    fault_type = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, info='turbine_fault_type的type值')
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)



class StatisticsSample(db.Model):
    __tablename__ = 'statistics_sample'
    __table_args__ = (
        db.Index('a', 'set_id', 'device_id', 'bin', 'create_time'),
    )

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False)
    device_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True)
    bin = db.Column(db.DateTime, nullable=False, index=True)
    evntemp_mean = db.Column(db.Float)
    powact_mean = db.Column(db.Float)
    powreact_mean = db.Column(db.Float)
    var_101_mean = db.Column(db.Float)
    var_102_mean = db.Column(db.Float)
    var_103_mean = db.Column(db.Float)
    var_107_mean = db.Column(db.Float)
    var_12031_mean = db.Column(db.Float)
    var_226_mean = db.Column(db.Float)
    var_246_mean = db.Column(db.Float)
    var_363_mean = db.Column(db.Float)
    var_382_mean = db.Column(db.Float)
    var_383_mean = db.Column(db.Float)
    var_407_mean = db.Column(db.Float)
    var_409_mean = db.Column(db.Float)
    var_412_mean = db.Column(db.Float)
    var_94_mean = db.Column(db.Float)
    winspd_mean = db.Column(db.Float)
    evntemp_rms = db.Column(db.Float)
    powact_rms = db.Column(db.Float)
    powreact_rms = db.Column(db.Float)
    var_101_rms = db.Column(db.Float)
    var_102_rms = db.Column(db.Float)
    var_103_rms = db.Column(db.Float)
    var_107_rms = db.Column(db.Float)
    var_12031_rms = db.Column(db.Float)
    var_226_rms = db.Column(db.Float)
    var_246_rms = db.Column(db.Float)
    var_363_rms = db.Column(db.Float)
    var_382_rms = db.Column(db.Float)
    var_383_rms = db.Column(db.Float)
    var_407_rms = db.Column(db.Float)
    var_409_rms = db.Column(db.Float)
    var_412_rms = db.Column(db.Float)
    var_94_rms = db.Column(db.Float)
    winspd_rms = db.Column(db.Float)
    evntemp_iqr = db.Column(db.Float)
    powact_iqr = db.Column(db.Float)
    powreact_iqr = db.Column(db.Float)
    var_101_iqr = db.Column(db.Float)
    var_102_iqr = db.Column(db.Float)
    var_103_iqr = db.Column(db.Float)
    var_107_iqr = db.Column(db.Float)
    var_12031_iqr = db.Column(db.Float)
    var_226_iqr = db.Column(db.Float)
    var_246_iqr = db.Column(db.Float)
    var_363_iqr = db.Column(db.Float)
    var_382_iqr = db.Column(db.Float)
    var_383_iqr = db.Column(db.Float)
    var_407_iqr = db.Column(db.Float)
    var_409_iqr = db.Column(db.Float)
    var_412_iqr = db.Column(db.Float)
    var_94_iqr = db.Column(db.Float)
    winspd_iqr = db.Column(db.Float)
    evntemp_std = db.Column(db.Float)
    powact_std = db.Column(db.Float)
    powreact_std = db.Column(db.Float)
    var_101_std = db.Column(db.Float)
    var_102_std = db.Column(db.Float)
    var_103_std = db.Column(db.Float)
    var_107_std = db.Column(db.Float)
    var_12031_std = db.Column(db.Float)
    var_226_std = db.Column(db.Float)
    var_246_std = db.Column(db.Float)
    var_363_std = db.Column(db.Float)
    var_382_std = db.Column(db.Float)
    var_383_std = db.Column(db.Float)
    var_407_std = db.Column(db.Float)
    var_409_std = db.Column(db.Float)
    var_412_std = db.Column(db.Float)
    var_94_std = db.Column(db.Float)
    winspd_std = db.Column(db.Float)
    evntemp_skew = db.Column(db.Float)
    powact_skew = db.Column(db.Float)
    powreact_skew = db.Column(db.Float)
    var_101_skew = db.Column(db.Float)
    var_102_skew = db.Column(db.Float)
    var_103_skew = db.Column(db.Float)
    var_107_skew = db.Column(db.Float)
    var_12031_skew = db.Column(db.Float)
    var_226_skew = db.Column(db.Float)
    var_246_skew = db.Column(db.Float)
    var_363_skew = db.Column(db.Float)
    var_382_skew = db.Column(db.Float)
    var_383_skew = db.Column(db.Float)
    var_407_skew = db.Column(db.Float)
    var_409_skew = db.Column(db.Float)
    var_412_skew = db.Column(db.Float)
    var_94_skew = db.Column(db.Float)
    winspd_skew = db.Column(db.Float)
    evntemp_kurt = db.Column(db.Float)
    powact_kurt = db.Column(db.Float)
    powreact_kurt = db.Column(db.Float)
    var_101_kurt = db.Column(db.Float)
    var_102_kurt = db.Column(db.Float)
    var_103_kurt = db.Column(db.Float)
    var_107_kurt = db.Column(db.Float)
    var_12031_kurt = db.Column(db.Float)
    var_226_kurt = db.Column(db.Float)
    var_246_kurt = db.Column(db.Float)
    var_363_kurt = db.Column(db.Float)
    var_382_kurt = db.Column(db.Float)
    var_383_kurt = db.Column(db.Float)
    var_407_kurt = db.Column(db.Float)
    var_409_kurt = db.Column(db.Float)
    var_412_kurt = db.Column(db.Float)
    var_94_kurt = db.Column(db.Float)
    winspd_kurt = db.Column(db.Float)
    evntemp_wf = db.Column(db.Float)
    powact_wf = db.Column(db.Float)
    powreact_wf = db.Column(db.Float)
    var_101_wf = db.Column(db.Float)
    var_102_wf = db.Column(db.Float)
    var_103_wf = db.Column(db.Float)
    var_107_wf = db.Column(db.Float)
    var_12031_wf = db.Column(db.Float)
    var_226_wf = db.Column(db.Float)
    var_246_wf = db.Column(db.Float)
    var_363_wf = db.Column(db.Float)
    var_382_wf = db.Column(db.Float)
    var_383_wf = db.Column(db.Float)
    var_407_wf = db.Column(db.Float)
    var_409_wf = db.Column(db.Float)
    var_412_wf = db.Column(db.Float)
    var_94_wf = db.Column(db.Float)
    winspd_wf = db.Column(db.Float)
    evntemp_crest = db.Column(db.Float)
    powact_crest = db.Column(db.Float)
    powreact_crest = db.Column(db.Float)
    var_101_crest = db.Column(db.Float)
    var_102_crest = db.Column(db.Float)
    var_103_crest = db.Column(db.Float)
    var_107_crest = db.Column(db.Float)
    var_12031_crest = db.Column(db.Float)
    var_226_crest = db.Column(db.Float)
    var_246_crest = db.Column(db.Float)
    var_363_crest = db.Column(db.Float)
    var_382_crest = db.Column(db.Float)
    var_383_crest = db.Column(db.Float)
    var_407_crest = db.Column(db.Float)
    var_409_crest = db.Column(db.Float)
    var_412_crest = db.Column(db.Float)
    var_94_crest = db.Column(db.Float)
    winspd_crest = db.Column(db.Float)
    evntemp_zc = db.Column(db.Float)
    powact_zc = db.Column(db.Float)
    powreact_zc = db.Column(db.Float)
    var_101_zc = db.Column(db.Float)
    var_102_zc = db.Column(db.Float)
    var_103_zc = db.Column(db.Float)
    var_107_zc = db.Column(db.Float)
    var_12031_zc = db.Column(db.Float)
    var_226_zc = db.Column(db.Float)
    var_246_zc = db.Column(db.Float)
    var_363_zc = db.Column(db.Float)
    var_382_zc = db.Column(db.Float)
    var_383_zc = db.Column(db.Float)
    var_407_zc = db.Column(db.Float)
    var_409_zc = db.Column(db.Float)
    var_412_zc = db.Column(db.Float)
    var_94_zc = db.Column(db.Float)
    winspd_zc = db.Column(db.Float)
    evntemp_cv = db.Column(db.Float)
    powact_cv = db.Column(db.Float)
    powreact_cv = db.Column(db.Float)
    var_101_cv = db.Column(db.Float)
    var_102_cv = db.Column(db.Float)
    var_103_cv = db.Column(db.Float)
    var_107_cv = db.Column(db.Float)
    var_12031_cv = db.Column(db.Float)
    var_226_cv = db.Column(db.Float)
    var_246_cv = db.Column(db.Float)
    var_363_cv = db.Column(db.Float)
    var_382_cv = db.Column(db.Float)
    var_383_cv = db.Column(db.Float)
    var_407_cv = db.Column(db.Float)
    var_409_cv = db.Column(db.Float)
    var_412_cv = db.Column(db.Float)
    var_94_cv = db.Column(db.Float)
    winspd_cv = db.Column(db.Float)
    evntemp_imp = db.Column(db.Float)
    powact_imp = db.Column(db.Float)
    powreact_imp = db.Column(db.Float)
    var_101_imp = db.Column(db.Float)
    var_102_imp = db.Column(db.Float)
    var_103_imp = db.Column(db.Float)
    var_107_imp = db.Column(db.Float)
    var_12031_imp = db.Column(db.Float)
    var_226_imp = db.Column(db.Float)
    var_246_imp = db.Column(db.Float)
    var_363_imp = db.Column(db.Float)
    var_382_imp = db.Column(db.Float)
    var_383_imp = db.Column(db.Float)
    var_407_imp = db.Column(db.Float)
    var_409_imp = db.Column(db.Float)
    var_412_imp = db.Column(db.Float)
    var_94_imp = db.Column(db.Float)
    winspd_imp = db.Column(db.Float)
    ongrid_mode = db.Column(db.String(20, 'utf8mb4_general_ci'))
    ongrid_unique = db.Column(db.String(50, 'utf8mb4_general_ci'))
    ongrid_nunique = db.Column(db.Integer)
    limitpowbool_mode = db.Column(db.String(10, 'utf8mb4_general_ci'))
    limitpowbool_unique = db.Column(db.String(20, 'utf8mb4_general_ci'))
    limitpowbool_nunique = db.Column(db.Integer)
    workmode_mode = db.Column(db.String(20, 'utf8mb4_general_ci'))
    workmode_unique = db.Column(db.String(150, 'utf8mb4_general_ci'))
    workmode_nunique = db.Column(db.Integer)
    totalfaultbool_mode = db.Column(db.String(10, 'utf8mb4_general_ci'))
    totalfaultbool_unique = db.Column(db.String(20, 'utf8mb4_general_ci'))
    totalfaultbool_nunique = db.Column(db.Integer)
    nobs = db.Column(db.Float)
    pv_c = db.Column(db.Float)
    pv_t = db.Column(db.Float)
    pv_ctt = db.Column(db.Float)
    create_time = db.Column(db.DateTime, nullable=False)



class TimedTask(db.Model):
    __tablename__ = 'timed_task'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False)
    status = db.Column(db.String(30, 'utf8mb4_general_ci'), nullable=False, info='状态，如create，added，summit，fail')
    func = db.Column(db.String(100, 'utf8mb4_general_ci'), nullable=False)
    type = db.Column(db.String(10, 'utf8mb4_general_ci'), nullable=False, info='任务类型')
    start_time = db.Column(db.DateTime, nullable=False, info='任务初始开始时间')
    function_parameter = db.Column(db.String(255, 'utf8mb4_general_ci'), info='传递给任务函数的参数')
    task_parameter = db.Column(db.String(255, 'utf8mb4_general_ci'), info='传递给scheduler的参数')
    username = db.Column(db.ForeignKey('user.username', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, index=True)
    update_time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', primaryjoin='TimedTask.username == User.username', backref='timed_tasks')



class TimedTaskLog(db.Model):
    __tablename__ = 'timed_task_log'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True, info='timed_task的记录id')
    status = db.Column(db.String(30, 'utf8mb4_general_ci'), nullable=False, info='事件')
    update_time = db.Column(db.DateTime, nullable=False, info='运行开始时间')



class TurbineFaultType(db.Model):
    __tablename__ = 'turbine_fault_type'

    id = db.Column(db.Integer, primary_key=True)
    is_offshore = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1=海上风机，0=陆上')
    name = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, info='故障名')
    cause = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, info='故障原因')
    value = db.Column(db.String(255, 'utf8mb4_general_ci'), info='取值')
    type = db.Column(db.String(10, 'utf8mb4_general_ci'), info='flag/fault/msg/alarm')
    var_names = db.Column(db.String(collation='utf8mb4_general_ci'), info='相关变量名')
    index = db.Column(db.String(255, 'utf8mb4_general_ci'), info="'code' 或具体var_name")
    time_span = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='绘图时故障开始时间前后时长，单位分钟')
    graph = db.Column(db.String(255, 'utf8mb4_0900_ai_ci'), nullable=False, server_default=db.FetchedValue(), info='绘图类')



class TurbineModelPoint(db.Model):
    __tablename__ = 'turbine_model_points'

    id = db.Column(db.Integer, primary_key=True)
    point_name = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False)
    var_name = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False, info='本地tdengine，set_id=20835的var_name，不变量')
    datatype = db.Column(db.String(10, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue())



class TurbineOperationMode(db.Model):
    __tablename__ = 'turbine_operation_mode'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False)
    descrption = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False)



class TurbineOutlierMonitor(db.Model):
    __tablename__ = 'turbine_outlier_monitor'

    id = db.Column(db.Integer, primary_key=True)
    system = db.Column(db.String(30, 'utf8mb4_general_ci'), nullable=False, info='部件名')
    type = db.Column(db.String(10, 'utf8mb4_general_ci'), nullable=False, info='温度 or 载荷')
    var_names = db.Column(db.Text(collation='utf8mb4_general_ci'), nullable=False, info='要监控的变量名；逗号分割')


class TurbineVariableBound(db.Model):
    __tablename__ = 'turbine_variable_bound'

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True, server_default=db.FetchedValue(), info='model_point对应字段')
    var_name = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, unique=True, info='model_point对应字段')
    name = db.Column(db.String(20, 'utf8mb4_general_ci'), info='需要显示的中文名称')
    lower_bound = db.Column(db.Float, nullable=False, server_default=db.FetchedValue(), info='报警下限，单位与model_point一致')
    upper_bound = db.Column(db.Float, nullable=False, server_default=db.FetchedValue(), info='报警上限，单位与model_point一致')



class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, index=True, info='用户名')
    password = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False, info='密码')
    privilege = db.Column(db.Integer, nullable=False, info='权限，1-具备账号管理功能，2-普通账户')



class WindfarmConfiguration(db.Model):
    __tablename__ = 'windfarm_configuration'

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, index=True)
    gearbox_ratio = db.Column(db.Float, nullable=False)
    is_offshore = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1=海上风机，0=陆上风机')
