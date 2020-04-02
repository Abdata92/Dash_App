import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd

app = dash.Dash(__name__)

df = pd.read_csv('D:/Projet perso/Dash_App/gapminder2007.csv',sep=";")

PAGE_SIZE = 5

app.layout = html.Div(
    className="row",
    children=[

        html.Div([

            dcc.Dropdown(id = 'dropdown-up',
                            options=[  
                                
                                     {'label': 'New York City', 'value': 'NYC'},
                                        {'label': 'Montreal', 'value': 'MTL'},
                                        {'label': 'San Francisco', 'value': 'SF'},
                                    ],
                            value= [] ,
                            multi=True
                        )

            ],
            id='table-paging-with-graph-container',
            className="five columns"
        ),

        html.Div(id = 'dd-output-container'),


        html.Div(
            dash_table.DataTable(
                id='table-paging-with-graph',
                columns=[
                    {"name": i, "id": i} for i in sorted(df.columns)
                ],
                page_current=0,
                page_size=20,
                page_action='custom',

                filter_action='custom',
                filter_query='',

                sort_action='custom',
                sort_mode='multi',
                sort_by=[]
            ),
            style={'height': 750, 'overflowY': 'scroll'},
            className='six columns'
        ),

         html.Div(id = 'dd2-output-container'),
        
    ]
)

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3






    

## remove filter result 

@app.callback(
    Output('dd-output-container', 'children'),
    [Input('dropdown-up', 'value'),
    Input('dropdown-up', 'options')
    ])
def update_output(value,options):
    return 'You have selected "{} {}"'.format(value,options)



@app.callback(
    [Output('dropdown-up', 'options'),Output('dropdown-up', 'value')],
    [Input('table-paging-with-graph', "filter_query")
    ])

def update_dropdown(filter):
    filtering_expressions = filter.split(' && ')
    #dff = df
    col_name_list = []
    filter_list = []
    operator_list = []
    for filter_part in filtering_expressions:
        col_name,operator,filter_value = split_filter_part(filter_part)
        print(type(filter_value))

        col_name_list.append(col_name)
        filter_list.append(filter_value)
        operator_list.append(operator)
       
        test = [{"label":str(col_name) +" " + str(operator) +" " + str(filter), "value": str(col_name) +" " + str(operator) +" " + str(filter)} for col_name, operator, filter in zip(col_name_list,operator_list, filter_list)]
        value = [filter for filter in filter_list]
        print(type(test))
    return test , value


@app.callback(
    Output('table-paging-with-graph', "data"),
    [Input('table-paging-with-graph', "page_current"),
     Input('table-paging-with-graph', "page_size"),
     Input('table-paging-with-graph', "sort_by"),
     Input('table-paging-with-graph', "filter_query"),
     Input('dropdown-up', 'value')
     ])

def update_table(page_current, page_size, sort_by, filter,value):
    filtering_expressions = filter.split(' && ')
    dff = df
    type(filter)
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]
    

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    return dff.iloc[ 
        page_current*page_size: (page_current + 1)*page_size
    ].to_dict('records')

    @app.callback(
    Output('table-paging-with-graph', "filter_query"),
    Input('dropdown-up', 'value')
    )
    def save_filter(value):
        if value is None:
            value = []
        return value




if __name__ == '__main__':
    app.run_server(debug=True)