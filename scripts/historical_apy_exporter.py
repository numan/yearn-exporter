import itertools
import logging
from datetime import datetime, timezone
from typing import Union

from yearn.apy import ApyError, get_samples
from yearn.apy.common import ApySamples
from yearn.historical_helper import export_historical, time_tracking
from yearn.networks import Network
from yearn.v1.registry import Registry as RegistryV1
from yearn.v1.vaults import VaultV1
from yearn.v2.registry import Registry as RegistryV2
from yearn.v2.vaults import Vault as VaultV2

logger = logging.getLogger("yearn.historical_vault_apy")
END_DATE = {
    Network.Mainnet: datetime(
        2020, 2, 12, tzinfo=timezone.utc
    ),  # first iearn deployment
}

v1_registry = RegistryV1()
v2_registry = RegistryV2()

def main():
    start = datetime.now(tz=timezone.utc)
    end = END_DATE[Network.Mainnet]
    data_query = 'apy'
    export_historical(
        start,
        end,
        export_chunk,
        export_snapshot,
        data_query
    )


def export_chunk(chunk, export_snapshot_func):

    for snapshot in chunk:
        samples: ApySamples = get_samples(now_time=snapshot)
        logger.info("Exporting snapshot for chunk")
        for vault in itertools.chain(v1_registry.vaults, v2_registry.vaults):
            export_snapshot_func(
                {
                    'vault': vault,
                    'samples': samples,
                    'exporter_name': 'historical_apy',
                }
            )


@time_tracking
def export_snapshot(vault: Union[VaultV1, VaultV2], samples: ApySamples, exporter_name):
    logger.info("exporting apy for vault")
    try:
        vault.export_apy(samples)
    except ApyError as e:
        logger.error("APY Error for %s at %s", vault, samples)
