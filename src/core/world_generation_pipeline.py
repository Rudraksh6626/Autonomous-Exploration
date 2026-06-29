"""
Backwards-compatible public module for world generation pipeline.

Implementation has been moved to core.pipeline_impl.WorldGenerationPipelineImpl.
This module keeps the original public class name so external imports continue
to work.
"""
from .pipeline_impl import WorldGenerationPipelineImpl

class WorldGenerationPipeline(WorldGenerationPipelineImpl):
    """
    Public class kept for compatibility. Subclasses the implementation so any
    existing isinstance checks against WorldGenerationPipeline still work.
    """
    pass

# Convenience factory kept for callers that prefer a function-style API.
def build_pipeline(*args, **kwargs):
    return WorldGenerationPipeline(*args, **kwargs)
