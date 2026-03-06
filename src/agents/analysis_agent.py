"""Analysis Agent - Research Analyst.

Responsible for synthesizing research findings, validating quality
and completeness, identifying gaps or contradictions, and generating
insights and recommendations. Can delegate back to the research agent
when additional information is needed.
"""

from crewai import Agent


def create_analysis_agent(llm=None) -> Agent:
    """Create and return the analysis agent.

    The analysis agent is a Research Analyst that synthesizes findings,
    identifies gaps, calculates quality scores, and can delegate back
    to the research agent if gaps are found.
    """
    agent_config = {
        "role": "Research Analyst",
        "goal": (
            "Synthesize and analyze research findings to produce a comprehensive "
            "analysis. Validate the quality and completeness of the research, "
            "identify any gaps, contradictions, or areas needing further investigation. "
            "Generate actionable insights and recommendations. If the research quality "
            "is insufficient, request additional research to fill gaps."
        ),
        "backstory": (
            "You are a senior research analyst with deep expertise in evaluating "
            "technical information. You excel at identifying patterns, spotting gaps "
            "in research, and synthesizing complex findings into clear insights. "
            "You have a keen eye for contradictions and always ensure research meets "
            "high quality standards before it proceeds to reporting. When you find "
            "gaps, you know exactly what additional research is needed and can "
            "delegate back to the research specialist."
        ),
        "tools": [],
        "allow_delegation": True,
        "verbose": True,
        "max_iter": 3,
        "max_retry_limit": 2,
    }

    if llm:
        agent_config["llm"] = llm

    return Agent(**agent_config)
