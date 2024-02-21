'''
作者：luosz
创建日期： 2024.02.18
描述：创建header，左侧导航栏，及主窗口（用于容纳page_container）
'''

#%% import
from collections import defaultdict
from typing import Container
import dash_mantine_components as dmc
from dash import Output, Input, clientside_callback, html, dcc, page_container, State, callback, ctx, no_update
from dash_iconify import DashIconify
import pandas as pd
from sqlalchemy import asc

#%% constant
THEME_PRIMARY_COLOR = 'indigo'
THEME_PRIMARY_SHADE = {'light': 5, 'dark':7}

HEADER_HEIGHT = '40px'
HEADER_PADDING_TOP = '8px'
HEADER_ICON_WIDTH = 20
HEADER_ICON_HORIZONTAL_SPACE = '5px'
HEADER_SWITCH_ICON_WIDTH = 10
HEADER_SWITCH_SIZE = 'xs'
HEADER_FONTSIZE = 'sm'
HEADER_BAGE_SIZE = 'lg'

NAVBAR_SIZE = '200px'
NAVBAR_SECTION_FONTSIZE = 'xs'
NAVBAR_ITEM_FONTSIZE = 'sm'

HEADER_LABEL = '海装风电数据分析助理系统'
HEADER_LABEL_ABBREATION =  'DAAS'
WINDFARM_NAME = '渤中风电场'

HEADER_MENU_FONTSIZE = '10px'
HEADER_MENU_ICON_WIDTH = 15

NAVBAR_ICONS = {
    "分析":"mdi:yin-yang",
    "调度":"mdi:traffic-light-outline",
}

MAIN_GRID_GUTTER = 5

MODAL_TITLE_FONTSIZE = 'sm'
MODAL_CONTENT_FONTSIZE = 'sm' 
MODAL_BUTTON_SIZE = 'xs' 
MODAL_COMPONENT_SIZE = 'xs' 
 
#%% fcuntion
def func_change_passwd():
    return dmc.Notification(
        title="密码已修改",
        id="simple-notify",
        action="show",
        message="Notifications in Dash, Awesome!",
        icon=DashIconify(icon="ic:round-celebration"),
        )
    
def func_build_table_content(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return table    
    

#%% component
def create_home_link(label):
    return  dmc.Anchor(
        href="/",
        underline=False,
        children=dmc.Badge(
            size=HEADER_BAGE_SIZE,
            radius='xs',
            children=label
            )
        )        

def create_header_first_column():
    return [
        dmc.MediaQuery(
            smallerThan="lg",
            styles={"display":"none"},
            children=dmc.Image(
                src="/assets/logo.png",
                width=50,
                radius=0,
                ),
            ),
        dmc.MediaQuery(
            smallerThan="lg",
            styles={"display":"none"},
            children=create_home_link(HEADER_LABEL),
            ),
        dmc.MediaQuery(
            largerThan="lg",
            styles={"display": "none"},
            children=create_home_link(HEADER_LABEL_ABBREATION),
            ),
        ]

def create_dropdown_menu_account():
    return dmc.Menu([
            dmc.MenuTarget(dmc.ActionIcon(
                variant="transparent",
                radius=30,
                color = dmc.theme.DEFAULT_COLORS['indigo'][3],
                children=DashIconify(icon="mdi:account-circle", width=HEADER_ICON_WIDTH),
                )),
            dmc.MenuDropdown([
                dmc.MenuItem(
                    "修改密码",
                    id='btn_change_passwd',
                    icon=DashIconify(icon="mdi:key-chain", width=HEADER_MENU_ICON_WIDTH),
                    style={'fontSize':HEADER_MENU_FONTSIZE}
                    ),
                dmc.MenuItem(
                    "管理账户",
                    id='btn_manage_user',
                    icon=DashIconify(icon="mdi:user-add", width=HEADER_MENU_ICON_WIDTH),
                    style={'fontSize':HEADER_MENU_FONTSIZE}
                    ),
                dmc.MenuItem(
                    "退出登录",
                    id='btn_logout',
                    icon=DashIconify(icon="mdi:logout", width=HEADER_MENU_ICON_WIDTH),
                    style={'fontSize':HEADER_MENU_FONTSIZE}
                    ),
                ]),
        ])

def create_header_last_column():
    return [
        dmc.Switch(
            offLabel=DashIconify(icon="radix-icons:moon", width=HEADER_SWITCH_ICON_WIDTH),
            onLabel=DashIconify(icon="radix-icons:sun", width=HEADER_SWITCH_ICON_WIDTH),
            checked=True,
            size=HEADER_SWITCH_SIZE,
            color='yellow',
            id='switch_color_scheme'
        ),
        dmc.Space(w=HEADER_ICON_HORIZONTAL_SPACE),
        create_dropdown_menu_account(),
        dmc.MediaQuery(
            largerThan="lg",
            styles={"display": "none"},
            children=[
                dmc.Space(w='5px'),
                dmc.ActionIcon(
                    DashIconify(icon="radix-icons:hamburger-menu", width=HEADER_ICON_WIDTH),
                    id="actionicon_navbar",
                    variant="transparent",
                    )
                ]
            ),
        dmc.Space(w=HEADER_ICON_HORIZONTAL_SPACE),                    
        ]

def create_header(nav_data):
    params = dict(p=0, m=0, span=4) 
    return dmc.Header(
        height=HEADER_HEIGHT,
        fixed=True,
        px=25,
        pt=HEADER_PADDING_TOP,
        children=dmc.Grid(
            h=HEADER_HEIGHT,
            children=[
                dmc.Col(
                    **params,
                    children=dmc.Center(
                        h='100%', style={'float':'left'}, 
                        children=create_header_first_column())
                    ),
                dmc.Col(
                    **params,
                    children=dmc.Center(
                        h='100%',
                        children=dmc.Text(WINDFARM_NAME, size=HEADER_FONTSIZE))
                    ),
                dmc.Col(
                    **params, 
                    children=dmc.Center(
                        h='100%', style={'float':'right'}, 
                        children=create_header_last_column())
                    ),                
                ]
            ),
        )

def create_side_nav_content(nav_data):
    ''' 根据secion_id排序，section_id格式为sectionName_x_y， 其中x用于section排序，y用于seciont内的item排序'''
    cols = ['path', 'section', 'item', 'section_order', 'item_order']
    df = pd.DataFrame(
        [[entry[i] for i in cols] for entry in nav_data if "section" in entry],
        columns=cols
        ).sort_values(['section_order', 'item_order'])

    links = []
    # for section, grp in df.groupby('section'):
    for section in df['section'].unique():
        grp = df[df['section']==section]
        links.append(
            dmc.Divider(
                labelPosition="left",
                label=[
                    DashIconify(
                        icon=NAVBAR_ICONS.get(section, "mdi:bug-outline"), width=15, style={"marginRight": 10}
                    ),
                    dmc.Text(section, size=NAVBAR_SECTION_FONTSIZE),
                ],
                my=10,
            )
        )        
        links.extend(
            [
                dmc.NavLink(label=dmc.Text(row['item'], size=NAVBAR_ITEM_FONTSIZE), href=row['path'], styles={"root": {"height": 30}})
                for _, row in grp.iterrows()
            ]
        )
        
    return dmc.Stack(spacing=0, px=25, children=[*links, dmc.Space(h=20)])

def create_side_navbar(nav_data):
    return dmc.Navbar(
        fixed=True,
        position={"top": HEADER_HEIGHT},
        width={"base": NAVBAR_SIZE},
        children=[
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                children=create_side_nav_content(nav_data),
            )
        ],
    )


def create_modal_change_passwd():
    '''
    不放在html.Div里会报错    
    '''
    return html.Div(dmc.Modal(
        title=dmc.Badge("修改密码", fz=MODAL_TITLE_FONTSIZE),
        id="mdl_change_passwd",
        zIndex=10000,
        size='xs',
        children=[
            dmc.Stack([
                dmc.PasswordInput(
                    label="旧密码",
                    placeholder="password",
                    style={"width": 200},
                    size=MODAL_COMPONENT_SIZE,
                    withAsterisk=True
                    ),
                dmc.PasswordInput(
                    label="新密码",
                    placeholder="password",
                    style={"width": 200},
                    size=MODAL_COMPONENT_SIZE,
                    withAsterisk=True
                    ),
                ]),
            dmc.Space(h=30),
            dmc.Group(
                position="right",
                children=[
                    dmc.Button("提交", id="btn_submit_change_passwd", size=MODAL_BUTTON_SIZE),
                    dmc.Button("关闭", id="btn_close_change_passwd", color='red', size=MODAL_BUTTON_SIZE),
                    ],
                ),
            ],
        ))

def create_modal_user_management():
    return html.Div(dmc.Modal(
        title=dmc.Badge("用户管理", fz=MODAL_TITLE_FONTSIZE),
        id="mdl_user_management",
        zIndex=10000,
        size='lg',
        children=[
            dmc.Group(
                align='start',
                children=[
                    dmc.Stack([
                        dmc.TextInput(
                            id='txt_username_user_management', 
                            style={"width": 200}, 
                            label="用户名:",
                            withAsterisk=True,
                            placeholder='username',
                            size=MODAL_COMPONENT_SIZE,
                            ),
                        dmc.PasswordInput(
                            id = 'txt_passwd_user_management',
                            placeholder="password",
                            style={"width": 200},
                            size=MODAL_COMPONENT_SIZE,
                            withAsterisk=True,
                            label="新密码",
                            ),
                        dmc.Select(
                            id='txt_role_user_management',
                            label='用户类型',
                            size=MODAL_COMPONENT_SIZE,
                            creatable=True,
                            withAsterisk=True,
                            style={"width": 200},
                            data=["管理员", "用户"],
                            value='管理员'
                            ),
                        dmc.Group(
                            position='apart',
                            style={"width": 200},
                            children=[
                                dmc.ActionIcon(
                                    id='txt_save_user_management',
                                    size=MODAL_COMPONENT_SIZE,
                                    variant="subtle",
                                    disabled=True,
                                    children=DashIconify(icon="mdi:content-save", width=30),
                                    color='indigo'
                                    ),
                                dmc.ActionIcon(
                                    id='txt_delete_user_management',
                                    size=MODAL_COMPONENT_SIZE,
                                    variant="subtle",
                                    disabled=True,
                                    children=DashIconify(icon="mdi:delete-alert-outline", width=30),
                                    color='red'
                                    )
                                ]                
                            )
                        ]),
                        dmc.Divider(orientation="vertical"),
                        html.Div(
                            style={"width": 330, 'height':300, 'overflow':'scroll'},
                            children=dmc.Table(
                                verticalSpacing='xs', 
                                striped=True,
                                highlightOnHover=True,
                                withBorder=True,
                                withColumnBorders=True,
                                fontSize =MODAL_COMPONENT_SIZE,
                                children=func_build_table_content(pd.DataFrame([['a','b']]*100, columns=['用户名','权限']))
                                )
                            
                        )
                    ]
                ),
            dmc.Space(h=30),
            dmc.Group(
                position="right",
                children=[
                    dmc.Button("关闭", color='red', id='btn_close_user_management', size=MODAL_BUTTON_SIZE),
                    ],
                ),
            ],
        ))

def create_navbar_drawer(nav_data):
    return dmc.Drawer(
        id="drawer_navbar",
        overlayOpacity=0.55,
        overlayBlur=3,
        zIndex=9,
        size=NAVBAR_SIZE,
        children=[
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                style={"height": "100vh"},
                pt=20,
                children=create_side_nav_content(nav_data),
            )
        ],
    )

#%% layout
def create_appshell(nav_data):
    return dmc.MantineProvider(  
        theme={'colorScheme':'light'},
        id='theme_provider',
        withGlobalStyles=True,
        withNormalizeCSS=True,
        children=dmc.MantineProvider(
            theme={'primaryColor':THEME_PRIMARY_COLOR, 'primaryShade':THEME_PRIMARY_SHADE},
            inherit=True,
            children=[
                dcc.Location(id='url', refresh='callback-nav'),
                dmc.NotificationsProvider(
                    children=[
                        html.Div(id="notficiation_container"),
                        create_header(nav_data),
                        create_navbar_drawer(nav_data),
                        create_modal_change_passwd(),
                        create_modal_user_management(),
                        dmc.MediaQuery(
                            smallerThan="xl",
                            styles={"display": "none"},
                            children=create_side_navbar(nav_data)
                            ),
                        html.Div(style={'height':'500px'}, children=page_container)
                        ]
                    )
                ]            
            )
        )

#%% callback
@callback(
    Output("theme_provider", "theme"),
    Input("switch_color_scheme", "checked"),
    prevent_initial_call=True    
)
def callback_change_theme(checked):
    return {"colorScheme":"light"} if checked else {"colorScheme":"dark"} 

@callback(
    Output("drawer_navbar", "opened"),
    Input("actionicon_navbar", "n_clicks"),
    prevent_initial_call=True  
)
def callback_open_navbar(n_clicks):
    return True

@callback(
    Output('mdl_change_passwd', 'opened'),
    Output('notficiation_container', 'children'),
    Input('btn_change_passwd', 'n_clicks'),
    Input('btn_submit_change_passwd', 'n_clicks'),
    Input('btn_close_change_passwd', 'n_clicks'),
    prevent_initial_call=True
    )
def callback_on_mdl_change_passwd(n1, n2, n3):
    _id = ctx.triggered_id
    opened = True if _id == 'btn_change_passwd' else False
    chldren = func_change_passwd() if _id == 'btn_submit_change_passwd' else no_update
    return opened, chldren

@callback(
    Output('mdl_user_management', 'opened'),
    Input('btn_manage_user', 'n_clicks'),
    Input('btn_close_user_management', 'n_clicks'),
    prevent_initial_call=True
    )
def callback_on_mdl_user_management(n1, n2):
    _id = ctx.triggered_id
    opened = True if _id == 'btn_manage_user' else False
    return opened