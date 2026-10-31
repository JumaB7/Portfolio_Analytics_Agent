from app.db.session import read_session_scope
from app.schemas.tools import RevenueByCategoryInput, RevenueByCategoryOutput
from app.services import analytics as analytics_service

TOOL_DEFINITIONS = [
    {
        "name": "get_revenue_by_category",
        "description": (
            "Rank product categories by revenue for an inclusive date range. "
            "Use when the user asks which category generated the most (or top) revenue. "
            "Returns has_data=false when empty; does not invent values."
        ),
        "parameters_model": RevenueByCategoryInput,
        "result_model": RevenueByCategoryOutput,
    }
]


def get_revenue_by_category_tool(
    params: RevenueByCategoryInput,
) -> RevenueByCategoryOutput:
    with read_session_scope() as session:
        return analytics_service.get_revenue_by_category(session, params)
