from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

root_dir = Path(__file__).parent
# Initialize the Dash app
app = Dash(__name__)

# Projects data
projects_df = pd.read_csv(root_dir / "src" / "projects.csv")
session_project_graph = go.Figure(
    data=[
        go.Bar(
            x=projects_df["secondary_ID"],
            y=projects_df["session_count"],
            text=projects_df["session_count"],
        )
    ]
)
session_project_graph.update_layout(
    title_text="Session count per Project",
    xaxis_title="Project Name",
    yaxis_title="Session Count",
    height=600,
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis_gridcolor="lightgray"
)
session_project_graph.update_traces(marker_color="#663171")
subject_project_graph = go.Figure(
    data=[
        go.Bar(
            x=projects_df["secondary_ID"],
            y=projects_df["subject_count"],
            text=projects_df["subject_count"],
        )
    ]
)
subject_project_graph.update_layout(
    title_text="Subject count per Project",
    xaxis_title="Project Name",
    yaxis_title="Subject Count",
    height=600,
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis_gridcolor="lightgray"
)
subject_project_graph.update_traces(marker_color="#cf3a36")


overall_description = (
    f"**Projects:** {len(projects_df)} - "
    f"**Subjects:** {projects_df["subject_count"].sum():,} - "
    f"**Subjects:** {projects_df["session_count"].sum():,}"
)

dropdown_options = [
    {"label": project["secondary_ID"], "value": project["ID"]}
    for _, project in projects_df.iterrows()
]


@app.callback(
    Output("session-by-year-graph", "figure"), [Input("project-dropdown", "value")]
)
def session_by_year_graph(selected_project):
    # Read the CSV data for the selected project
    df = pd.read_csv(root_dir / "src" / "projects" / f"{selected_project}.csv")

    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Group by year and count sessions
    sessions_by_year = df.groupby(df["date"].dt.year).size().reset_index(name="count")

    # Create a new bar chart for sessions by year
    fig = go.Figure(
        data=[
            go.Bar(
                x=sessions_by_year["date"], y=sessions_by_year["count"], name="Sessions"
            )
        ],
    )

    # Update layout
    fig.update_layout(
        title_text="Sessions by Year",
        height=400,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_gridcolor="lightgray",
        yaxis_tickformat=",d",
    )
    fig.update_xaxes(type='category')
    fig.update_traces(marker_color="#ea7428")
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Number of Sessions")

    if sessions_by_year["count"].max()<=10:
        fig.update_layout(
            yaxis_dtick=1,
        )

    return fig


@app.callback(Output("modality-graph", "figure"), [Input("project-dropdown", "value")])
def modality_graph(selected_project):
    # Read the CSV data for the selected project
    df = pd.read_csv(root_dir / "src" / "projects" / f"{selected_project}.csv")

    # Group by modalities and count sessions
    modalities = df.groupby(df["modality"]).size().reset_index(name="count")

    # Create a new bar chart for modalities
    fig = go.Figure(
        data=[
            go.Bar(x=modalities["modality"], y=modalities["count"], name="Modalities")
        ],
    )

    # Update layout
    fig.update_layout(
        title_text="Modalities",
        height=400,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_gridcolor="lightgray",
        yaxis_tickformat=",d",
    )

    fig.update_traces(marker_color="#e2998a")
    fig.update_xaxes(title_text="Modalities")
    fig.update_yaxes(title_text="Number of Sessions")

    if modalities["count"].max()<=10:
        fig.update_layout(
            yaxis_dtick=1,
        )

    return fig


@app.callback(
    Output("project-description", "children"), [Input("project-dropdown", "value")]
)
def project_description(selected_project):
    # Read the CSV data for the selected project
    row = projects_df.loc[projects_df["ID"] == selected_project].copy().reset_index()
    description = (
        f"**Project ID:** {selected_project}\n\n"
        f"**Name:** {row.name[0]}\n\n"
        f"**Description:** {row.description[0] if isinstance(row.description[0], str) else "No description available"}\n\n"
        f"**Session Count:** {row.session_count[0]:,}\n\n"
        f"**Subject Count:** {row.subject_count[0]:,}\n\n"
    )
    return description


# Bar chart for sessions by year
fig_session_by_year = session_by_year_graph(dropdown_options[0]["value"])
# Bar chart for modalities
fig_modalities = modality_graph(dropdown_options[0]["value"])

# Layout of the app
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(children="BIMCV-XNAT Dashboard", style={"fontSize": "32px", "fontWeight": "bold"}),
                html.H2(children="Overview", style={"fontSize": "26px", "fontWeight": "bold"}),
                dcc.Markdown(
                    id="overall-description", 
                    children=overall_description, 
                    style={
                        "width": "90%", 
                        "padding": "1px",
                        "fontSize": "24px",
                        "text-align": "center",
                        "backgroundColor": "#f0f0f0",
                    }
                ),
                html.Div(
                    children=[
                        dcc.Graph(
                            id="session-project-graph",
                            figure=session_project_graph,
                            style={"width": "50%"}
                        ),
                        dcc.Graph(
                            id="subject-project-graph",
                            figure=subject_project_graph,
                            style={"width": "50%"}
                        ),
                    ],
                    style={
                        "display": "flex",
                    },
                ),
                html.H2(children="Project Details", style={"fontSize": "26px", "fontWeight": "bold"}),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.H3(children="Choose a project:", style={"padding-right": "20px", "verticalAlign": "top"}),
                                        dcc.Dropdown(
                                            id="project-dropdown",
                                            options=dropdown_options,
                                            value=dropdown_options[0]["value"],
                                            clearable=False,
                                            style={"width": "80%"}
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                    },
                                ),
                                dcc.Markdown(
                                    id="project-description", 
                                    children="", 
                                    style={
                                        "width": "90%", 
                                        "padding": "10px",
                                        "verticalAlign": "middle",
                                        "backgroundColor": "#f0f0f0",
                                    }
                                ),
                            ],
                        ),
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id="session-by-year-graph",
                                    figure=fig_session_by_year,
                                    style={"width": "50%"}
                                ),
                                dcc.Graph(
                                    id="modality-graph", 
                                    figure=fig_modalities,
                                    style={"width": "50%"}    
                                ),
                            ],
                            style={
                                "display": "flex",
                            },
                        ),
                    ],
                ),
            ],
        ),
    ],
    style={
        "width": "50%",
        "padding": "20px",
        "font-family": "Arial", 
        "font-size": "14px", 
        "color": "#333"
    },
)


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
