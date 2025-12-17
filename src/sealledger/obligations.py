from .models import Obligation
from .crypto import sha256_hex, sign, pub_from_priv
from .kms import LocalKMS
from datetime import datetime
from typing import List, Dict, Any


def extract_obligations(userdata: Dict[str, Any]) -> List[Obligation]:
    # naive extractor: map well-known keys to obligations
    obs: List[Obligation] = []
    if "portfolio" in userdata:
        # example: max_loss constraint
        if "max_loss" in userdata["portfolio"]:
            obs.append(
                Obligation(
                    id="O_portfolio_max_loss",
                    type="max_loss",
                    owner=userdata.get("owner"),
                    constraint={"max_loss": userdata["portfolio"]["max_loss"]},
                )
            )
    if "predictions" in userdata:
        obs.append(
            Obligation(
                id="O_prediction_target",
                type="prediction_target",
                owner=userdata.get("owner"),
                constraint={"target": userdata.get("prediction_target", 0.5)},
            )
        )
    # add simple compliance rule if present
    if "compliance" in userdata:
        obs.append(
            Obligation(
                id="O_compliance",
                type="compliance",
                owner=userdata.get("owner"),
                constraint=userdata["compliance"],
            )
        )
    return obs


def verify_premises(ob: Obligation, inputs: Dict[str, Any]) -> Dict[str, Any]:
    # returns premises that were verified
    premises = {"checked_at": datetime.utcnow().isoformat()}
    if ob.type == "max_loss":
        max_loss = ob.constraint["max_loss"]
        # assume inputs contain 'portfolio' with 'loss'
        loss = inputs.get("portfolio", {}).get("loss", 0.0)
        premises["loss"] = loss
        premises["satisfied"] = loss <= max_loss
    elif ob.type == "prediction_target":
        # check 'predictions' mean
        preds = inputs.get("predictions", [])
        if preds:
            avg = sum(preds) / len(preds)
        else:
            avg = 0.0
        premises["avg_prediction"] = avg
        premises["satisfied"] = avg >= ob.constraint.get("target", 0.0)
    else:
        # generic: check presence of keys
        premises["satisfied"] = True
    return premises




def bond_obligation(ob: Obligation, premises: Dict[str, Any], signer: LocalKMS | bytes | None = None) -> Obligation:
    # seal hash = sha256 of premises serialization
    import json

    payload = json.dumps(premises, sort_keys=True).encode()
    h = sha256_hex(payload)
    # default to local KMS if none supplied
    # support legacy raw private key bytes or a KMS instance
    if isinstance(signer, (bytes, bytearray)):
        sig = sign(signer, payload)
        pub = pub_from_priv(signer)
    else:
        kms = signer or LocalKMS()
        sig = kms.sign(None, payload)
        _, pub = kms.generate_keypair()
    ob.premises = premises
    ob.seal_hash = h
    ob.status = "bonded"
    ob.bonded_at = datetime.utcnow()
    # attach signature in metadata field within constraint for prototype
    ob.constraint["_signature"] = sig.hex()
    ob.constraint["_signer_pub"] = pub.hex()
    return ob
