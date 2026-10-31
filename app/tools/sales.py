from app.db.session import read_session_scope
from app.schemas.tools import SalesSummaryInput, SalesSummaryOutput
from app.services import analytics as analytics_service

TOOL_DEFINITIONS = [
    {
        "name": "get_sales_summary",
        "description": (
            "Return total revenue, order count, and units sold for an inclusive "
            "date range over the synthetic demo e-commerce dataset. "
            "Use when the user asks for total sales or revenue for a period. "
            "Does not invent values; returns has_data=false when empty."
        ),
        "parameters_model": SalesSummaryInput,
        "result_model": SalesSummaryOutput,
    }
]


def get_sales_summary_tool(params: SalesSummaryInput) -> SalesSummaryOutput:
    """Allowlisted tool entrypoint — validates inputs then runs a read-only query."""
    with read_session_scope() as session:
        return analytics_service.get_sales_summary(session, params)
