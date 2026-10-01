from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Iterable


IDENTITY_PATTERNS=(
    re.compile(r"https?://",re.I),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I),
    re.compile(r"\b(?:[a-z0-9-]+\.)+[a-z]{2,}\b",re.I),
    re.compile(r"\b(?:acct|account|zone|resource|token)[-_ ]?[a-z0-9]{8,}\b",re.I),
    re.compile(r"\b[a-f0-9]{32,}\b",re.I),
)


@dataclass(frozen=True)
class CommandHit:
    command:str
    summary:str

    def validate(self)->None:
        if not isinstance(self.command,str) or not self.command.startswith("cf ") or len(self.command)>300:
            raise ValueError("command_invalid")
        if not isinstance(self.summary,str) or not self.summary or len(self.summary)>500:
            raise ValueError("summary_invalid")


def validate_anonymous_query(query:str)->str:
    if not isinstance(query,str) or not query.strip() or len(query)>500:
        raise ValueError("query_invalid")
    q=" ".join(query.split())
    if any(p.search(q) for p in IDENTITY_PATTERNS):
        raise ValueError("query_contains_identity_or_locator")
    return q


def compact_discovery_projection(
    *,
    query:str,
    ranked_hits:Iterable[CommandHit],
    commands_metadata_bytes:int,
    schema_metadata_bytes:int,
    top_k:int=5,
)->dict:
    q=validate_anonymous_query(query)
    if type(commands_metadata_bytes) is not int or commands_metadata_bytes<=0:
        raise ValueError("commands_metadata_bytes_invalid")
    if type(schema_metadata_bytes) is not int or schema_metadata_bytes<=0:
        raise ValueError("schema_metadata_bytes_invalid")
    if type(top_k) is not int or not 1<=top_k<=5:
        raise ValueError("top_k_invalid")

    hits=list(ranked_hits)
    for hit in hits:
        hit.validate()
    visible=hits[:top_k]
    payload=[{"command":h.command,"summary":h.summary} for h in visible]
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    full=commands_metadata_bytes+schema_metadata_bytes
    return {
        "schema":"ftsl.capability-discovery-surface/v0.1",
        "query":q,
        "result_count":len(payload),
        "results":payload,
        "visible_bytes":len(raw),
        "full_metadata_bytes":full,
        "surface_fraction":len(raw)/full,
        "surface_reduction_ratio":full/max(1,len(raw)),
        "next_step":"EXACT_SCHEMA",
        "execution_authority":"NONE",
        "query_sent_to_provider":False,
        "discovery_local_only":True,
        "projection_sha256":"sha256:"+sha256(raw).hexdigest(),
    }


def classify_cli_effect(
    *,
    returncode:int,
    mutation_expected:bool,
    semantic_receipt:str|None,
    stderr:str="",
)->dict:
    if type(returncode) is not int:
        raise ValueError("returncode_invalid")
    if semantic_receipt not in {None,"APPLIED","NO_EFFECT","DRY_RUN","UNKNOWN"}:
        raise ValueError("semantic_receipt_invalid")

    aborted="aborted" in stderr.lower()
    if returncode!=0:
        status="FAILED"
        reason="nonzero_returncode"
    elif semantic_receipt=="APPLIED":
        status="APPLIED"
        reason="semantic_receipt"
    elif semantic_receipt in {"NO_EFFECT","DRY_RUN"}:
        status=semantic_receipt
        reason="semantic_receipt"
    elif aborted:
        status="NO_EFFECT"
        reason="explicit_abort_text"
    elif mutation_expected:
        status="UNKNOWN"
        reason="zero_exit_without_effect_receipt"
    else:
        status="PROCESS_OK"
        reason="zero_exit_nonmutation"

    return {
        "schema":"ftsl.cli-effect-classification/v0.1",
        "status":status,
        "reason":reason,
        "returncode":returncode,
        "mutation_expected":mutation_expected,
        "semantic_receipt":semantic_receipt,
        "returncode_is_effect_proof":False,
        "authority_effect":"NONE",
    }
