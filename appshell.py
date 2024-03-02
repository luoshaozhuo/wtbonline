'''
作者：luosz
创建日期： 2024.02.18
描述：创建header，左侧导航栏，及主窗口（用于容纳page_container）
'''

#%% import
import dash_mantine_components as dmc
from dash import Output, Input, html, dcc, page_container, State, callback, ctx, no_update
from dash_iconify import DashIconify
import pandas as pd
from flask_login import current_user, logout_user

from wtbonline import configure as cfg

#%% constant
NAVBAR_SIZE = '200px'
NAVBAR_SECTION_FONTSIZE = 'xs'
NAVBAR_ITEM_FONTSIZE = 'sm'

NAVBAR_ICONS = {
    "分析":"mdi:microscope",
    "探索":"mdi:airballoon-outline",
    "识别":"mdi:yin-yang",
    "任务调度":"mdi:account-tie-hat-outline",
}

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
            size=cfg.HEADER_BAGE_SIZE,
            ml=10,
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
                height=20,
                radius=0,
                ),
            ),
        dmc.MediaQuery(
            smallerThan="lg",
            styles={"display":"none"},
            children=create_home_link(cfg.HEADER_LABEL),
            ),
        dmc.MediaQuery(
            largerThan="lg",
            styles={"display": "none"},
            children=create_home_link(cfg.HEADER_LABEL_ABBREATION),
            ),
        ]

def create_dropdown_menu_account():
    return dmc.Menu([
            dmc.MenuTarget(dmc.ActionIcon(
                id='menu',
                display='none',
                variant="transparent",
                radius=30,
                color = dmc.theme.DEFAULT_COLORS['indigo'][3],
                children=DashIconify(icon="mdi:account-circle", width=cfg.HEADER_ICON_WIDTH),
                )),
            dmc.MenuDropdown([
                dmc.MenuItem(
                    "修改密码",
                    id='btn_change_passwd',
                    icon=DashIconify(icon="mdi:key-chain", width=cfg.HEADER_MENU_ICON_WIDTH),
                    style={'fontSize':cfg.HEADER_MENU_FONTSIZE},
                    href='/user/password',
                    ),
                dmc.MenuItem(
                    "管理账户",
                    display='none',
                    id='btn_manage_user',
                    icon=DashIconify(icon="mdi:user-add", width=cfg.HEADER_MENU_ICON_WIDTH),
                    style={'fontSize':cfg.HEADER_MENU_FONTSIZE},
                    href='/user/administrate',
                    ),
                dmc.MenuItem(
                    "退出登录",
                    id='btn_logout',
                    icon=DashIconify(icon="mdi:logout", width=cfg.HEADER_MENU_ICON_WIDTH),
                    style={'fontSize':cfg.HEADER_MENU_FONTSIZE}
                    ),
                ]),
        ])

def create_header_last_column():
    return [
        dmc.Space(w=cfg.HEADER_ICON_HORIZONTAL_SPACE),
        create_dropdown_menu_account(),
        dmc.MediaQuery(
            largerThan="lg",
            styles={"display": "none"},
            children=[
                dmc.Space(w='5px'),
                dmc.ActionIcon(
                    DashIconify(icon="radix-icons:hamburger-menu", width=cfg.HEADER_ICON_WIDTH),
                    id="actionicon_navbar",
                    variant="transparent",
                    )
                ]
            ),
        dmc.Space(w=cfg.HEADER_ICON_HORIZONTAL_SPACE),                    
        ]

def create_header(nav_data):
    params = dict(p=0, m=0, span=4) 
    return dmc.Header(
        height=cfg.HEADER_HEIGHT,
        fixed=True,
        px=25,
        pt=cfg.HEADER_PADDING_TOP,
        children=dmc.Grid(
            h=cfg.HEADER_HEIGHT,
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
                        children=dmc.Text(cfg.WINDFARM_NAME, size=cfg.HEADER_FONTSIZE))
                    ),
                dmc.Col(
                    **params, 
                    children=dmc.Center(
                        h='100%', style={'float':'right'}, 
                        children=create_header_last_column()
                        )
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
        id='navbar',
        display='none',
        fixed=True,
        position={"top": cfg.HEADER_HEIGHT},
        width={"base": NAVBAR_SIZE},
        children=[
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                children=create_side_nav_content(nav_data),
            )
        ],
    )

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
            theme={'primaryColor':cfg.THEME_PRIMARY_COLOR, 'primaryShade':cfg.THEME_PRIMARY_SHADE},
            inherit=True,
            children=[
                dcc.Location(id='url', refresh='callback-nav'),
                dmc.NotificationsProvider(
                    children=[
                        html.Div(id="notficiation_container"),
                        create_header(nav_data),
                        create_navbar_drawer(nav_data),
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
    Output("drawer_navbar", "opened"),
    Input("actionicon_navbar", "n_clicks"),
    prevent_initial_call=True  
)
def callback_open_navbar(n_clicks):
    return True

@callback(
    Output('url', 'pathname'),
    Output('menu', 'display'),
    Output('navbar', 'display'),
    Output('btn_manage_user', 'display'),
    Input('url', 'pathname'),
    Input('btn_logout', 'n_clicks'),
    )
def callback_show_Page(pathname, n):
    if pathname == '/login' or not current_user.is_authenticated or ctx.triggered_id=='btn_logout':
        pathname = '/login'
        display = 'none'
        btn_manage_user = 'none'
    else:
        btn_manage_user = 'flex' if current_user.username=='admin' else 'none'
        display = 'inline'
    return pathname, display, display, btn_manage_user
