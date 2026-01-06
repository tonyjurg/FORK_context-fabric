"""MCP resource definitions for Context-Fabric.

Resources provide read-only data that agents can access via URIs.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from cfabric.results import NodeInfo, CorpusInfo

from cfabric_mcp.corpus_manager import corpus_manager

logger = logging.getLogger("cfabric_mcp.resources")


def get_corpus_resource(corpus_name: str) -> str:
    """Get corpus information as a resource.

    URI: corpus://{corpus_name}
    """
    logger.debug("resource: corpus://%s", corpus_name)
    CF, api = corpus_manager.get(corpus_name)
    path = CF.locations[-1] if CF.locations else ""
    info = CorpusInfo.from_api(api, corpus_name, str(path))
    return info.to_json()


def get_node_resource(corpus_name: str, node_id: int) -> str:
    """Get node information as a resource.

    URI: corpus://{corpus_name}/node/{node_id}
    """
    logger.debug("resource: corpus://%s/node/%d", corpus_name, node_id)
    api = corpus_manager.get_api(corpus_name)
    info = NodeInfo.from_api(
        api,
        node_id,
        include_text=True,
        include_section=True,
        include_slots=True,
    )
    return info.to_json()


def get_feature_list_resource(corpus_name: str) -> str:
    """Get list of features as a resource.

    URI: corpus://{corpus_name}/features
    """
    logger.debug("resource: corpus://%s/features", corpus_name)
    api = corpus_manager.get_api(corpus_name)
    return json.dumps(
        {
            "node_features": api.Fall(warp=False),
            "edge_features": api.Eall(warp=False),
        }
    )


def get_node_types_resource(corpus_name: str) -> str:
    """Get node type information as a resource.

    URI: corpus://{corpus_name}/types
    """
    logger.debug("resource: corpus://%s/types", corpus_name)
    api = corpus_manager.get_api(corpus_name)
    C = api.C

    types = []
    for level_info in C.levels.data:
        ntype, avg_slots, min_node, max_node = level_info
        types.append(
            {
                "type": ntype,
                "count": int(max_node - min_node + 1),
                "avg_slots": float(avg_slots),
                "min_node": int(min_node),
                "max_node": int(max_node),
            }
        )

    return json.dumps({"types": types})
