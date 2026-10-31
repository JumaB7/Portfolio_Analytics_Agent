from app.db.session import session_scope
from app.schemas.tools import CompareSalesPeriodsInput, CompareSalesPeriodsOutput
from app.services import analytics as analytics_service

TOOL_DEFINITIONS = [
    {
        "name": "compare_sales_periods",
        "description": (
            "Compare total sales between two inclusive date ranges "
            "(for example current month vs previous month). "
            "Returns revenue change and percent change when previous revenue is non-zero. "
            "Use for month-over-month or period comparison questions."
        ),
        "parameters_model": CompareSalesPeriodsInput,
        "result_model": CompareSalesPeriodsOutput,
    }
]


def compare_sales_periods_tool(
    params: CompareSalesPeriodsInput,
) -> CompareSalesPeriodsOutput:
    with session_scope() as session:
        result = analytics_service.compare_sales_periods(session, params)
        session.expunge_all()
        return result
