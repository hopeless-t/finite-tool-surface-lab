from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable


STATUSES = frozenset({
    "SUPPORTED",
    "PARTIAL",
    "DEFERRED",
    "NEEDS_EQUIVALENT",
    "UNSUPPORTED",
})


@dataclass(frozen=True)
class CompatibilityItem:
    feature_id: str
    status: str
    evidence_id: str | None = None
    note: str = ""

    def validate(self) -> None:
        if not isinstance(self.feature_id, str) or not self.feature_id or len(self.feature_id) > 200:
            raise ValueError("feature_id_invalid")
        if self.status not in STATUSES:
            raise ValueError("status_invalid")
        if self.evidence_id is not None and (
            not isinstance(self.evidence_id, str)
            or not self.evidence_id
            or len(self.evidence_id) > 300
        ):
            raise ValueError("evidence_id_invalid")
        if not isinstance(self.note, str) or len(self.note) > 1000:
            raise ValueError("note_invalid")


def compatibility_profile(
    *,
    source_surface: str,
    target_surface: str,
    items: Iterable[CompatibilityItem],
) -> dict:
    if not isinstance(source_surface, str) or not source_surface:
        raise ValueError("source_surface_invalid")
    if not isinstance(target_surface, str) or not target_surface:
        raise ValueError("target_surface_invalid")

    rows=list(items)
    if not rows:
        raise ValueError("items_empty")
    for row in rows:
        row.validate()
    if len({r.feature_id for r in rows}) != len(rows):
        raise ValueError("duplicate_feature_id")

    counts={status:0 for status in sorted(STATUSES)}
    supported_with_evidence=0
    for row in rows:
        counts[row.status]+=1
        if row.status=="SUPPORTED" and row.evidence_id is not None:
            supported_with_evidence+=1

    denominator=len(rows)
    supported=counts["SUPPORTED"]
    strict_supported_fraction=supported/denominator

    executable_rows=[
        {
            "feature_id":r.feature_id,
            "status":r.status,
            "evidence_id":r.evidence_id,
            "note":r.note,
        }
        for r in sorted(rows,key=lambda x:x.feature_id)
    ]
    canonical=json.dumps(
        executable_rows,sort_keys=True,separators=(",",":"),ensure_ascii=False
    ).encode("utf-8")
    return {
        "schema":"ftsl.compatibility-profile/v0.1",
        "source_surface":source_surface,
        "target_surface":target_surface,
        "feature_count":denominator,
        "status_counts":counts,
        "strict_supported_fraction":strict_supported_fraction,
        "supported_with_evidence":supported_with_evidence,
        "all_supported_features_evidenced":supported_with_evidence==supported,
        "profile_sha256":"sha256:"+sha256(canonical).hexdigest(),
        "items":executable_rows,
        "substitution_authority":"NONE",
        "compatibility_is_not_identity":True,
    }


def substitution_gate(profile: dict, required_features: Iterable[str]) -> dict:
    if not isinstance(profile,dict) or profile.get("schema")!="ftsl.compatibility-profile/v0.1":
        raise ValueError("profile_invalid")
    required=list(required_features)
    if not required:
        raise ValueError("required_features_empty")
    by_id={row["feature_id"]:row for row in profile["items"]}

    missing=[]
    partial=[]
    unsupported=[]
    unevidenced=[]
    for feature in required:
        row=by_id.get(feature)
        if row is None:
            missing.append(feature)
            continue
        status=row["status"]
        if status=="PARTIAL":
            partial.append(feature)
        elif status in {"DEFERRED","NEEDS_EQUIVALENT","UNSUPPORTED"}:
            unsupported.append(feature)
        elif status=="SUPPORTED" and row["evidence_id"] is None:
            unevidenced.append(feature)

    if missing:
        status,reason="BLOCKED","required_feature_missing"
    elif unsupported:
        status,reason="BLOCKED","required_feature_not_supported"
    elif partial:
        status,reason="REVIEW","required_feature_partial"
    elif unevidenced:
        status,reason="REVIEW","supported_feature_unevidenced"
    else:
        status,reason="COMPATIBLE","all_required_features_supported_with_evidence"

    return {
        "schema":"ftsl.substitution-gate/v0.1",
        "status":status,
        "reason":reason,
        "missing":sorted(missing),
        "partial":sorted(partial),
        "unsupported":sorted(unsupported),
        "unevidenced":sorted(unevidenced),
        "substitution_authority":"NONE",
    }
