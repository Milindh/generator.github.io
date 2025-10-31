"""
Agents package for multi-agent cover letter generation
"""

from .producer_agent import generate_cover_letter, refine_cover_letter
from .critic_agent import critique_cover_letter
from .workflow import (
    run_single_iteration_workflow, 
    get_final_cover_letter, 
    get_workflow_summary
)

__all__ = [
    'generate_cover_letter',
    'refine_cover_letter',
    'critique_cover_letter',
    'run_single_iteration_workflow',
    'get_final_cover_letter',
    'get_workflow_summary'
]