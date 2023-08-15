from app.crud.base import BaseCRUD
from app.models import Donation


class DonationCRUD(BaseCRUD):
    pass


donation_crud = DonationCRUD(Donation)