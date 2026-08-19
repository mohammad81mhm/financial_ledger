from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class TransferReceivedNotification:
    """Payload pushed to a receiver when a peer transfer completes.

    Attributes:
        sender_username (str): Username of the user who sent the transfer.
        amount (str): Transfer amount serialized as a decimal string.
        currency (str): Currency code of the receiver wallet.
        wallet_id (int): Primary key of the credited receiver wallet.
        transaction_id (str): UUID of the completed transfer transaction.
    """

    sender_username: str
    amount: int
    currency: str
    wallet_id: int
    transaction_id: str

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation of this notification.

        Returns:
            dict: Notification fields keyed by attribute name.
        """
        return asdict(self)
