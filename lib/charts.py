"""Shared Plotly styling constants and helpers."""

TEXT_COLOR = '#1F2937'

BLUE_SCALE = [[0, '#D9E5F1'], [0.5, '#6B88A8'], [1, '#2E4A6B']]


def style_horizontal_bar(fig, height):
    """
    Apply the standard horizontal-bar layout used across the dashboard.
    Mirrors the original update_layout block byte-for-byte.
    """
    fig.update_layout(
        yaxis={
            'categoryorder': 'total ascending',
            'tickfont': dict(color=TEXT_COLOR, size=12),
            'title_font': dict(color=TEXT_COLOR, size=13),
        },
        height=height,
        title_font_size=20,
        font=dict(color=TEXT_COLOR, size=12),
        xaxis=dict(
            tickfont=dict(color=TEXT_COLOR, size=12),
            title_font=dict(color=TEXT_COLOR, size=13),
        ),
        coloraxis_showscale=False,
    )
