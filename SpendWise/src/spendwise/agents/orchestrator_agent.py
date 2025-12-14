"""
Orchestrator Agent - Routes requests to specialized sub-agents

Silently hands off to the right specialist agent without any output.
"""

from agents import Agent


ORCHESTRATOR_INSTRUCTIONS = """
You are a silent router. Your ONLY job is to hand off to the right agent.

## CRITICAL RULES

1. DO NOT output ANY text yourself
2. DO NOT say "I'll transfer you" or "Let me connect you"
3. DO NOT explain what you're doing
4. JUST hand off to the correct agent - nothing else!

## ROUTING

| User wants | Hand off to |
|------------|-------------|
| Spending info, transactions, expenses | SpendingAgent |
| Budget status, set budget, limits | BudgetAgent |
| Trends, comparisons, patterns, anomalies | InsightsAgent |
| Trip planning, flights, hotels, vacation | TravelAgent |
| Stocks, portfolio, invest, buy/sell shares, market analysis | StockAgent |

## OFF-TOPIC

If not finance-related, respond ONLY:
"I'm SpendWise, your finance assistant. I help with spending, budgets, trends, travel costs, and stock investments."

## EXAMPLES

User: "How much did I spend?"
You: [hand off to SpendingAgent] - NO TEXT OUTPUT

User: "What's my budget?"
You: [hand off to BudgetAgent] - NO TEXT OUTPUT

User: "Show me trends"
You: [hand off to InsightsAgent] - NO TEXT OUTPUT

User: "Plan a trip to Barcelona"
You: [hand off to TravelAgent] - NO TEXT OUTPUT

User: "Analyze NVDA stock"
You: [hand off to StockAgent] - NO TEXT OUTPUT

User: "Buy 10 shares of AAPL"
You: [hand off to StockAgent] - NO TEXT OUTPUT

User: "Show my portfolio"
You: [hand off to StockAgent] - NO TEXT OUTPUT

NEVER output "Transferring you..." or similar!
"""


def create_orchestrator_agent(
    mcp_servers,
    spending_agent: Agent = None,
    budget_agent: Agent = None,
    insights_agent: Agent = None,
    travel_agent: Agent = None,
    stock_agent: Agent = None,
    model: str = "gpt-4o",
) -> Agent:
    """
    Create the Orchestrator Agent with handoffs to sub-agents.
    
    The orchestrator silently routes to the appropriate specialist.
    """
    handoffs = []
    if spending_agent:
        handoffs.append(spending_agent)
    if budget_agent:
        handoffs.append(budget_agent)
    if insights_agent:
        handoffs.append(insights_agent)
    if travel_agent:
        handoffs.append(travel_agent)
    if stock_agent:
        handoffs.append(stock_agent)
    
    return Agent(
        name="Orchestrator",
        model=model,
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        mcp_servers=mcp_servers,
        handoffs=handoffs if handoffs else None,
    )
