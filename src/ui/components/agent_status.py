"""
Agent Status Component - Componentă pentru afișarea statusului agenților
"""

import streamlit as st
from typing import Dict


def render_agent_status(status: str, agent_name: str) -> str:
    """
    Randează status agent cu HTML.
    
    Args:
        status: Status agent (ACTIVE, IDLE, MONITORING, ERROR)
        agent_name: Nume agent (ex: "Agent 1")
    
    Returns:
        HTML string pentru status
    """
    status_lower = status.lower()
    if status_lower == 'active':
        return f'<div class="status-active">{agent_name}<br><strong>{status}</strong></div>'
    elif status_lower == 'idle':
        return f'<div class="status-idle">{agent_name}<br><strong>{status}</strong></div>'
    elif status_lower == 'monitoring':
        return f'<div class="status-monitoring">{agent_name}<br><strong>{status}</strong></div>'
    else:
        return f'<div class="status-error">{agent_name}<br><strong>{status}</strong></div>'


def render_agent_status_row(agent_statuses: Dict[str, str]) -> None:
    """
    Randează rândul cu status-urile tuturor agenților.
    
    Args:
        agent_statuses: Dict cu status-uri {'agent1': 'ACTIVE', 'agent2': 'IDLE', ...}
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        agent1_status = agent_statuses.get('agent1', 'IDLE')
        st.markdown(render_agent_status(agent1_status, "Agent 1"), unsafe_allow_html=True)
        st.caption("Data Collection")
    
    with col2:
        agent2_status = agent_statuses.get('agent2', 'IDLE')
        st.markdown(render_agent_status(agent2_status, "Agent 2"), unsafe_allow_html=True)
        st.caption("Decision")
    
    with col3:
        agent3_status = agent_statuses.get('agent3', 'IDLE')
        st.markdown(render_agent_status(agent3_status, "Agent 3"), unsafe_allow_html=True)
        st.caption("Execution")
