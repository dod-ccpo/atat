import json
import os
import re

import pendulum
import requests


class CRLNotFoundError(Exception):
    pass


class CRLParseError(Exception):
    pass


MODIFIED_TIME_BUFFER = 15 * 60


CRL_LIST = [
    (
        "https://crl.gds.disa.mil/crl/DODROOTCA2.crl",
        "305b310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311630140603550403130d446f4420526f6f742043412032",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODROOTCA3.crl",
        "305b310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311630140603550403130d446f4420526f6f742043412033",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODROOTCA4.crl",
        "305b310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311630140603550403130d446f4420526f6f742043412034",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODROOTCA5.crl",
        "305b310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311630140603550403130d446f4420526f6f742043412035",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_33.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442049442043412d3333",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_34.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442049442043412d3334",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDSWCA_35.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f442049442053572043412d3335",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDSWCA_36.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f442049442053572043412d3336",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDSWCA_37.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f442049442053572043412d3337",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDSWCA_38.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f442049442053572043412d3338",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_39.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442049442043412d3339",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_40.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442049442043412d3430",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_41.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442049442043412d3431",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_42.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442049442043412d3432",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_43.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442049442043412d3433",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_44.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442049442043412d3434",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDSWCA_45.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f442049442053572043412d3435",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDSWCA_46.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f442049442053572043412d3436",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDSWCA_47.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f442049442053572043412d3437",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDSWCA_48.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f442049442053572043412d3438",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_49.crl",
        "305a310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493115301306035504030c0c444f442049442043412d3439",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_50.crl",
        "305a310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493115301306035504030c0c444f442049442043412d3530",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_51.crl",
        "305a310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493115301306035504030c0c444f442049442043412d3531",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_52.crl",
        "305a310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493115301306035504030c0c444f442049442043412d3532",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODIDCA_59.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442049442043412d3539",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODSWCA_53.crl",
        "305a310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493115301306035504030c0c444f442053572043412d3533",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODSWCA_54.crl",
        "305a310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493115301306035504030c0c444f442053572043412d3534",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODSWCA_55.crl",
        "305a310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493115301306035504030c0c444f442053572043412d3535",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODSWCA_56.crl",
        "305a310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493115301306035504030c0c444f442053572043412d3536",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODSWCA_57.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442053572043412d3537",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODSWCA_58.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442053572043412d3538",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODSWCA_60.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442053572043412d3630",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODSWCA_61.crl",
        "305a310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311530130603550403130c444f442053572043412d3631",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_33.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f4420454d41494c2043412d3333",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_34.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f4420454d41494c2043412d3334",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_39.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f4420454d41494c2043412d3339",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_40.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f4420454d41494c2043412d3430",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_41.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f4420454d41494c2043412d3431",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_42.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f4420454d41494c2043412d3432",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_43.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f4420454d41494c2043412d3433",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_44.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f4420454d41494c2043412d3434",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_49.crl",
        "305d310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493118301606035504030c0f444f4420454d41494c2043412d3439",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_50.crl",
        "305d310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493118301606035504030c0f444f4420454d41494c2043412d3530",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_51.crl",
        "305d310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493118301606035504030c0f444f4420454d41494c2043412d3531",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_52.crl",
        "305d310b300906035504061302555331183016060355040a0c0f552e532e20476f7665726e6d656e74310c300a060355040b0c03446f44310c300a060355040b0c03504b493118301606035504030c0f444f4420454d41494c2043412d3532",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODEMAILCA_59.crl",
        "305d310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311830160603550403130f444f4420454d41494c2043412d3539",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODINTEROPERABILITYROOTCA1.crl",
        "306c310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49312730250603550403131e446f4420496e7465726f7065726162696c69747920526f6f742043412031",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODINTEROPERABILITYROOTCA2.crl",
        "306c310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49312730250603550403131e446f4420496e7465726f7065726162696c69747920526f6f742043412032",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/USDODCCEBINTEROPERABILITYROOTCA1.crl",
        "3074310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49312f302d06035504031326555320446f44204343454220496e7465726f7065726162696c69747920526f6f742043412031",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/USDODCCEBINTEROPERABILITYROOTCA2.crl",
        "3074310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49312f302d06035504031326555320446f44204343454220496e7465726f7065726162696c69747920526f6f742043412032",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODNIPRINTERNALNPEROOTCA1.crl",
        "3075310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f4431143012060355040b130b496e7465726e616c4e5045312830260603550403131f446f44204e49505220496e7465726e616c204e504520526f6f742043412031",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODNPEROOTCA1.crl",
        "305f310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f44310c300a060355040b1303504b49311a301806035504031311446f44204e504520526f6f742043412031",  # pragma: allowlist secret
    ),
    (
        "https://crl.gds.disa.mil/crl/DODWCFROOTCA1.crl",
        "3063310b300906035504061302555331183016060355040a130f552e532e20476f7665726e6d656e74310c300a060355040b1303446f443110300e060355040b130757434620504b49311a301806035504031311446f442057434620526f6f742043412031",  # pragma: allowlist secret
    ),
]


JSON_CACHE = "crl_locations.json"


def _deserialize_cache_items(cache):
    return {bytes.fromhex(der): data for (der, data) in cache.items()}


def load_crl_locations_cache(crl_dir):
    json_location = "{}/{}".format(crl_dir, JSON_CACHE)
    with open(json_location, "r") as json_file:
        cache = json.load(json_file)
        return _deserialize_cache_items(cache)


def serialize_crl_locations_cache(crl_dir, crl_list=CRL_LIST):
    crl_cache = {}
    for crl_uri, crl_issuer in crl_list:
        crl_path = crl_local_path(crl_dir, crl_uri)
        if os.path.isfile(crl_path):
            crl_cache[crl_issuer] = crl_path

    json_location = "{}/{}".format(crl_dir, JSON_CACHE)
    with open(json_location, "w") as json_file:
        json.dump(crl_cache, json_file)

    return {bytes.fromhex(k): v for k, v in crl_cache.items()}


def crl_local_path(out_dir, crl_location):
    name = re.split("/", crl_location)[-1]
    crl = os.path.join(out_dir, name)
    return crl


def existing_crl_modification_time(crl):
    if os.path.exists(crl):
        prev_time = os.path.getmtime(crl)
        buffered = prev_time + MODIFIED_TIME_BUFFER
        mod_time = prev_time if pendulum.now().timestamp() < buffered else buffered
        dt = pendulum.from_timestamp(mod_time, tz="UTC")
        return dt.format("ddd, DD MMM YYYY HH:mm:ss zz")

    else:
        return False


def write_crl(out_dir, target_dir, crl_location):
    crl = crl_local_path(out_dir, crl_location)
    existing = crl_local_path(target_dir, crl_location)
    options = {"stream": True}
    mod_time = existing_crl_modification_time(existing)
    if mod_time:
        options["headers"] = {"If-Modified-Since": mod_time}

    with requests.get(crl_location, **options) as response:
        if response.status_code > 399:
            raise CRLNotFoundError()

        if response.status_code == 304:
            return (False, existing)

        with open(crl, "wb") as crl_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    crl_file.write(chunk)

    return (True, existing)


def remove_bad_crl(out_dir, crl_location):
    crl = crl_local_path(out_dir, crl_location)
    os.remove(crl)


def log_error(logger, error_string, crl_location):
    if logger:
        logger.error(
            f"{error_string}: Error downloading {crl_location}, removing file and continuing anyway"
        )


def refresh_crl(out_dir, target_dir, crl_uri, logger):
    logger.info("updating CRL from {}".format(crl_uri))
    try:
        was_updated, crl_path = write_crl(out_dir, target_dir, crl_uri)
        if was_updated:
            logger.info("successfully synced CRL from {}".format(crl_uri))
        else:
            logger.info("no updates for CRL from {}".format(crl_uri))

        return crl_path
    except requests.exceptions.ChunkedEncodingError:
        log_error(logger, "ChunkedEncodingError", crl_uri)
        remove_bad_crl(out_dir, crl_uri)
    except CRLNotFoundError:
        log_error(logger, "CRLNotFoundError", crl_uri)


def sync_crls(tmp_location, final_location):
    crl_cache = {}
    for crl_uri, crl_issuer in CRL_LIST:
        crl_path = refresh_crl(tmp_location, final_location, crl_uri, logger)
        crl_cache[crl_issuer] = crl_path

    json_location = "{}/{}".format(final_location, JSON_CACHE)
    with open(json_location, "w") as json_file:
        json.dump(crl_cache, json_file)


if __name__ == "__main__":
    import sys
    import logging

    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s]:%(levelname)s: %(message)s"
    )
    logger = logging.getLogger()
    logger.info("Updating CRLs")
    try:
        tmp_location = sys.argv[1]
        final_location = sys.argv[2]
        sync_crls(tmp_location, final_location)
    except Exception as err:
        logger.exception("Fatal error encountered, stopping")
        sys.exit(1)
    logger.info("Finished updating CRLs")
