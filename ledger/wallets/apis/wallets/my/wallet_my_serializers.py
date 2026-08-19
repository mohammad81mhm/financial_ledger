from ledger.wallets.apis.wallets.define.wallet_define_serializers import WalletOutputSerializer


class WalletMyOutputSerializer(WalletOutputSerializer):
    """Wallet fields returned by the list-my-wallets API."""

    class Meta(WalletOutputSerializer.Meta):
        pass
