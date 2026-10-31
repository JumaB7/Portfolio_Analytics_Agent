from app.db.session import session_scope
from app.schemas.tools import ProductPerformanceInput, ProductPerformanceOutput
from app.services import analytics as analytics_service

TOOL_DEFINITIONS = [
    {
        "name": "get_product_performance",
        "description": (
            "Rank products by revenue for an inclusive date range. "
            "Set sort=highest for top sellers or sort=lowest for weakest sellers. "
            "Use for questions about best/worst products. Does not invent values."
        ),
        "parameters_model": ProductPerformanceInput,
        "result_model": ProductPerformanceOutput,
    }
]


def get_product_performance_tool(
    params: ProductPerformanceInput,
) -> ProductPerformanceOutput:
    with session_scope() as session:
        result = analytics_service.get_product_performance(session, params)
        session.expunge_all()
        return result
