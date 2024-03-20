from datetime import datetime, timedelta
from typing import Tuple, Type, TypeVar, List

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import (ObjectDoesNotExist,
                                    MultipleObjectsReturned,
                                    ValidationError)
from django.db.models import Q
from django.db.models import Model
from asgiref.sync import sync_to_async

from btr.bookings.models import Booking
from btr.tg_bot.utils import exceptions as e
from btr.users.models import SiteUser
from btr.workhours.models import WorkHours

T = TypeVar("T", bound=Model)


class AsyncTools:
    """
    A utility class with methods for connect async and sync context, mostly
     between Aiogram(async) and Django ORM(sync) for CRUD operation.
    """
    @sync_to_async
    def get_queryset(self, user: SiteUser(), **kwargs) -> list:
        """
        Get a QuerySet of Booking objects based on the provided kw arguments.

        Args:
            user (SiteUser): The user for whom to retrieve bookings.
            **kwargs: Additional keyword arguments to filter the queryset.

        Returns:
            list: The filtered Booking queryset.
        """
        queryset = Booking.objects.filter(rider=user.id)

        for field, value in kwargs.items():
            lookup = {field: value}
            queryset = queryset.filter(**lookup)

        queryset = queryset.exclude(status__in=[_('completed'), _('canceled')])
        return list(queryset)

    @sync_to_async
    def get_object(self, model: Type[T], load_prefetch=None, **kwargs) -> T:
        """
        Get a Model object based on the provided keyword arguments.

        Args:
            model (Type[T]): The Model class.
            load_prefetch (string | None): Load added bounded objects.
            **kwargs: Keyword arguments to filter the object.

        Returns:
            T: The retrieved Model object.
        """
        if load_prefetch:
            obj = model.objects.prefetch_related(load_prefetch).get(**kwargs)
        else:
            obj = model.objects.get(**kwargs)
        return obj

    @sync_to_async
    def modify_booking(self, pk: str, **kwargs) -> None:
        """
        Modify booking attributes based on provided keyword arguments.

        Args:
            pk (str): The primary key of the booking to be modified.
            **kwargs: Additional keyword arguments representing fields
             and their new values.
        """
        booking = Booking.objects.get(pk=pk)
        for field, value in kwargs.items():
            setattr(booking, field, value)
        booking.save()

    @sync_to_async
    def check_available_field(self, user_input: str) -> bool:
        """
        Check if the provided user input (username, email, or phone number)
         is available.

        Args:
            user_input (str): The user input to check.

        Returns:
            bool: True if the user input is available, False otherwise.
        """
        login = user_input.lower()
        try:
            SiteUser.objects.get(
                Q(username=login) |
                Q(email=login) |
                Q(phone_number=login)
            )
            raise e.UserAlreadyExists
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return True

    @sync_to_async
    def create_user(self, **kwargs) -> str:
        """
        Create a new user with the provided keyword arguments.

        Args:
            **kwargs: Keyword arguments for creating the user
             (e.g., username, email, etc.).

        Returns:
            str: The randomly generated password for the new user.
        """
        password = SiteUser.objects.make_random_password(length=8)
        user = SiteUser.objects.create(**kwargs)
        user.set_password(password)
        user.save()
        return password

    @sync_to_async
    def reset_password(self, **kwargs) -> str:
        """
        Reset the user's password and return the new randomly
         generated password.

        Args:
            **kwargs: Keyword arguments to identify the user
             (e.g., username, email, etc.).

        Returns:
            str: The newly generated password.
        """
        user = SiteUser.objects.get(**kwargs)
        password = SiteUser.objects.make_random_password(length=8)
        user.set_password(password)
        user.save()
        return password

    @sync_to_async
    def create_booking(self, **kwargs) -> str:
        """
        Create a new booking with the provided attributes.

        Args:
            **kwargs: Keyword arguments for creating the booking
             (e.g., rider, date, etc.).

        Returns:
            str: The ID of the newly created booking.
        """
        user = SiteUser.objects.get(pk=kwargs.get('rider'))
        kwargs['rider'] = user
        booking = Booking.objects.create(**kwargs)
        booking.save()
        return str(booking.id)

    async def edit_booking(self, **kwargs) -> None:
        """
        Edit an existing booking with the provided attributes.

        Args:
            **kwargs: Keyword arguments for editing the booking
             (e.g., pk, date, start, end, bikes, etc.).

        Returns:
            None
        """
        pk = kwargs.get('pk')
        edited_data = {
            'booking_data': kwargs.get('date'),
            'start_time': kwargs.get('start'),
            'end_time': kwargs.get('end'),
            'bike_count': kwargs.get('bikes'),
            'status': _('pending')
        }
        await self.modify_booking(pk, **edited_data)

    async def get_user_info(self, **kwargs) -> dict:
        """
        Get all user info.

        Args:
            **kwargs: Additional keyword arguments for querying the user.

        Returns:
            dict: A dictionary containing user information with keys:
                - 'pk': User ID
                - 'name': First name
                - 'username': Username
                - 'email': Email address
                - 'phone': Phone number (as a string)

        Raises:
            UserDoesNotExists: If the user does not exist.
        """
        try:
            user = await self.get_object(SiteUser, **kwargs)
            return {
                'pk': user.id,
                'name': user.first_name,
                'username': user.username,
                'email': user.email,
                'phone': str(user.phone_number),
            }
        except ObjectDoesNotExist:
            raise e.UserDoesNotExists

    async def check_password(self, password: str, **kwargs) -> None:
        """
        Check if the provided password is correct for the user.

        Args:
            password (str): The password to check.
            **kwargs: Additional keyword arguments for querying the user.

        Raises:
            WrongPassword: If the password is incorrect.
            UserDoesNotExists: If the user does not exist.
        """
        try:
            user = await self.get_object(SiteUser, **kwargs)
            if user.check_password(password):
                return None
            raise e.WrongPassword
        except ObjectDoesNotExist:
            raise e.UserDoesNotExists

    async def get_user_bookings(self, **kwargs) -> dict:
        """
        Find and get all bookings for the user.

        Args:
            **kwargs: Additional keyword arguments for querying the user.

        Returns:
            dict: A dictionary containing booking data with keys:
                - 'bookings_data': List of formatted booking information
                - 'bookings_id': List of booking IDs (as strings)
        """
        user = await self.get_object(SiteUser, **kwargs)
        bookings = await self.get_queryset(user, rider=user.id)
        bookings_ids = [str(booking.id) for booking in bookings]
        bookings_view = []
        for booking in bookings:
            book = _(
                '<em>🔹 ID: <strong>{id}</strong> | <strong>{date}</strong>'
                ' | <strong>{start}</strong> - <strong>{end}</strong></em>'
            ).format(
                id=booking.id,
                date=booking.booking_date,
                start=booking.start_time.strftime('%H:%M'),
                end=booking.end_time.strftime('%H:%M'),
            )
            bookings_view.append(book)
        return {'bookings_data': bookings_view, 'bookings_id': bookings_ids}

    async def create_account(self, data: dict) -> str:
        """
        Create a new user account with the provided user information.

        Args:
            data (dict): A dictionary containing user information
             (e.g., name, username, phone, email, status).

        Returns:
            str: The randomly generated password for the new user account.
        """
        user_info = {
            'first_name': data.get('name'),
            'username': data.get('username'),
            'phone_number': data.get('phone'),
            'email': data.get('email'),
            'status': data.get('status'),
        }
        password = await self.create_user(**user_info)
        return password

    async def make_booking(self, data: dict, is_admin=False) -> str:
        """
        Create a new booking with the provided data.

        Args:
            data (dict): A dictionary containing booking information
             (e.g., pk, date, start, end, bikes, etc.).
            is_admin (bool, optional): Indicates whether the booking
             is confirmed by an admin. Defaults to False.

        Returns:
            str: The ID of the newly created booking.
        """
        booking = {
            'rider': data.get('pk'),
            'booking_date': data.get('date'),
            'start_time': data.get('start'),
            'end_time': data.get('end'),
            'bike_count': data.get('bikes'),
            'status': _('confirmed') if is_admin else _('pending'),
        }
        booking_id = await self.create_booking(**booking)
        return booking_id

    async def get_booking_info(self, load_prefetch=None, **kwargs) -> dict:
        """
        Check and return booking information based on the primary key.

        Args:
            load_prefetch (string | None): Load bounded object.
            **kwargs: Additional keyword arguments for querying the booking.

        Returns:
            dict: A dictionary containing booking information with keys:
                - 'date': Booking date in the format "YYYY Month DD"
                - 'start': Start time of the booking (formatted as HH:MM)
                - 'end': End time of the booking (formatted as HH:MM)
                - 'status': Booking status
                - 'bikes': Number of bikes booked
                - 'phone': Phone number of the rider (as a string)
                - 'f_phone': Foreign phone number (as a string)
                - 'rider_id': Bounded user (as a string) or None.

        Raises:
            NotExistedId: If the booking with the given primary key
             does not exist.
        """
        try:
            booking = await self.get_object(
                Booking, load_prefetch=load_prefetch, **kwargs)
            booking_info = {
                'date': booking.booking_date.strftime('%Y-%B-%d'),
                'clean_date': booking.booking_date.strftime('%Y-%m-%d'),
                'start': booking.start_time.strftime('%H:%M'),
                'end': booking.end_time.strftime('%H:%M'),
                'status': booking.status,
                'bikes': booking.bike_count,
                'f_phone': str(booking.foreign_number),
                'rider_id': booking.rider.id if load_prefetch else None,
            }
            translated_month = self.get_friendly_date(booking_info.get('date'))
            booking_info['friendly_date'] = translated_month
            return booking_info
        except ObjectDoesNotExist:
            raise e.NotExistedId

    @staticmethod
    def get_friendly_date(date: str) -> str:
        """
        Translate the month name in the given date to the desired language.

        Args:
            date (str): Date in the format "YYYY Month DD"

        Returns:
            str: Translated month name (e.g., "March" in English)
        """
        parts = date.split('-')
        year, month, day = parts
        plural_month = f'{month}s'
        return f'{day} {_(plural_month)}, {year}'

    async def get_excluded_slot(self, email: str, date: str) -> tuple:
        """
        Checks and retrieves all available times
         (if the user already has a reservation for that date).

        Args:
            email (str): The email address of the user.
            date (str): The date for which to retrieve the booking.

        Returns:
            tuple: A tuple containing the start time and end time of the
             existed booking (None if there are no bookings for this date).
        """
        user = await self.get_object(SiteUser, email=email)
        queryset = await self.get_queryset(user, rider=user.id,
                                           booking_date=date)
        booking = queryset[-1]
        if booking:
            return booking.start_time, booking.end_time

    async def get_available_status(self, **kwargs) -> List:
        """
        Determine the available status transition for a booking based
         on its current status.

        Args:
            **kwargs: Keyword arguments to identify the booking
             (e.g., pk, date, etc.).

        Returns:
            str: The updated status (either 'confirmed' or 'canceled').

        Raises:
            ObjectDoesNotExist: If the booking does not exist.
        """
        booking = await self.get_object(Booking, **kwargs)
        status = booking.status
        if status == _('confirmed'):
            return [str(_('canceled')),]
        elif status == _('canceled'):
            return [str(_('confirmed')),]
        elif status == _('pending'):
            return [str(_('confirmed')), str(_('canceled'))]
        raise ObjectDoesNotExist

    async def change_booking_status(self, status: str, pk: str) -> None:
        """
        Change the status of a booking identified by its primary key.

        Args:
            status (str): The new status to set for the booking
             (e.g., 'confirmed', 'canceled', etc.).
            pk (str): The primary key of the booking.

        Returns:
            None
        """
        booking = await self.get_object(Booking, pk=pk)
        booking.status = status
        await sync_to_async(booking.save)()


class SlotsFinder:
    """
    A utility class for finding available time slots.

    Attributes:
        FRIDAY (int): The day of the week corresponding to Friday (5).

    Args:
        date (str): The date for which slots need to be found.
    """

    FRIDAY = 5

    def __init__(self, date: str):
        self.date = date

    @staticmethod
    def get_workhours() -> dict:
        """
        Get work time ranges from database.

        Returns:
            dict: dictionary with default open time slots.
        """
        ordinary_slots = WorkHours.objects.get(day='Workday')
        weekend_slots = WorkHours.objects.get(day='Weekend')
        return {
            'ordinary_slots': (ordinary_slots.open, ordinary_slots.close),
            'weekend_slots': (weekend_slots.open, weekend_slots.close),
        }

    @staticmethod
    @sync_to_async
    def get_workhours_as() -> dict:
        """
        Get work time ranges from database asynchronous(for bot usage).

        Returns:
            dict: dictionary with default open time slots.
        """
        ordinary_slots = WorkHours.objects.get(day='Workday')
        weekend_slots = WorkHours.objects.get(day='Weekend')
        return {
            'ordinary_slots': (ordinary_slots.open, ordinary_slots.close),
            'weekend_slots': (weekend_slots.open, weekend_slots.close),
        }

    def is_weekend(self) -> bool:
        """
        Check if the given date falls on a weekend.

        Returns:
            bool: True if the date is a weekend (Saturday or Sunday),
             False otherwise.
        """
        f_date = datetime.strptime(self.date, "%Y-%m-%d")
        return f_date.weekday() >= self.FRIDAY

    def get_booked_slots(self) -> List[Tuple]:
        """
        Retrieve busy time ranges from the database.

        Returns:
            list: A list of strings representing booked time slots
             in the format "start_time-end_time".
        """
        bookings = (Booking.objects.filter(booking_date=self.date).exclude(
            status='canceled')
        )
        return [(book.start_time, book.end_time) for book in bookings]

    def get_booked_slots_for_edit(self, excluded_slot: tuple) -> List[Tuple]:
        """
        Retrieve busy time ranges excluding the current range.

        Args:
            excluded_slot (tuple): A tuple representing the current time range
             (start_time, end_time).

        Returns:
            list: A list of strings representing booked time slots
             that do not overlap with the excluded range.
        """
        exc_start, exc_end = excluded_slot
        bookings = (Booking.objects.filter(booking_date=self.date).exclude(
            status='canceled')
        )
        return [(book.start_time, book.end_time) for book in bookings if
                (book.start_time >= exc_end or book.end_time <= exc_start)]

    @staticmethod
    def get_free_intervals(working_hours: Tuple,
                           booked_slots: List[Tuple]) -> List[Tuple]:
        """
        Calculate available time slots based on booked seconds.

        Args:
            working_hours (tuple): A tuple of working time (open-close)
            booked_slots (list): A list of tuples representing
             booked time slots in seconds.

        Returns:
            list: A list of tuples representing available time slots
             in the format (start_time, end_time).
        """
        if not booked_slots:
            return [tuple(map(lambda x: x.strftime('%H:%M'), working_hours))]

        # combine time with date for further operations
        combined_bookings = [(datetime.combine(datetime.today(), start),
                              datetime.combine(datetime.today(), end)) for
                             start, end in booked_slots]

        # set service intervals around bookings by 1 hour
        booked_intervals = [((start - timedelta(hours=1)).time(),
                             (end + timedelta(hours=1)).time()) for start, end
                            in combined_bookings]

        free_intervals = []

        # sort booked slots by start time before open time
        booked_intervals.sort(key=lambda x: x[0])

        # add initial free slot
        if working_hours[0] < booked_intervals[0][0]:
            free_intervals.append((working_hours[0], booked_intervals[0][0]))

        # find free intervals between booked slots
        for i in range(len(booked_intervals) - 1):
            if booked_intervals[i][1] < booked_intervals[i + 1][0]:
                free_intervals.append(
                    (booked_intervals[i][1], booked_intervals[i + 1][0]))

        # add final free interval after close time
        if booked_intervals[-1][1] < working_hours[1]:
            free_intervals.append((booked_intervals[-1][1], working_hours[1]))

        return [(start.strftime('%H:%M'), end.strftime('%H:%M')) for start, end
                in free_intervals]

    def find_available_slots(self, excluded_slot: Tuple = None) -> List[Tuple]:
        """
        Get a list of available time slots (for django view).

        Args:
            excluded_slot (tuple, optional): A tuple representing
             the current time range (start_time, end_time). Defaults to None.

        Returns:
            list: A list of tuples representing available time slots
             in the format (start_time, end_time).
        """
        if self.date.split('-')[-1] == '0':
            return []
        slots = self.get_workhours()
        if self.is_weekend():
            working_hours = slots.get('weekend_slots')
        else:
            working_hours = slots.get('ordinary_slots')
        if not excluded_slot:
            booked_slots = self.get_booked_slots()
        else:
            booked_slots = self.get_booked_slots_for_edit(excluded_slot)
        available_slots = self.get_free_intervals(working_hours, booked_slots)
        return available_slots

    async def find_available_slots_as(self, excluded_slot=None) -> list:
        """
        Get a list of available time slots (for bot).

        Args:
            excluded_slot (tuple, optional): A tuple representing
             the current time range (start_time, end_time). Defaults to None.

        Returns:
            list: A list of tuples representing available time slots
             in the format (start_time, end_time).
        """
        get_booking_slots_as = sync_to_async(self.get_booked_slots)
        get_slots_for_edit = sync_to_async(self.get_booked_slots_for_edit)
        slots = await self.get_workhours_as()
        if self.is_weekend():
            working_hours = slots.get('weekend_slots')
        else:
            working_hours = slots.get('ordinary_slots')
        try:
            if not excluded_slot:
                booked_slots = await get_booking_slots_as()
            else:
                booked_slots = await get_slots_for_edit(excluded_slot)
            available_slots = self.get_free_intervals(working_hours,
                                                      booked_slots)
            return available_slots
        except ValidationError:
            return []


class LoadCalc:
    """
    A utility class for calculating load-related information.

    Attributes:
        FRIDAY (int): The day of the week corresponding to Friday (5).
        ORDINARY_DAY_HOURS (int): The number of hours in an ordinary
         workday (6).
        WEEKEND_DAY_HOURS (int): The number of hours in a weekend workday (8).

    Args:
        calendar (list): A list representing the calendar data.
        year (int): The year for which load calculations are performed.
        month (int): The month for which load calculations are performed.
    """
    FRIDAY = 5
    ORDINARY_DAY_HOURS = 6
    WEEKEND_DAY_HOURS = 8

    def __init__(self, calendar: list, year: int, month: int):
        self.calendar = calendar
        self.year = year
        self.month = month

    def get_day_load(self, date: str) -> int:
        """
        Calculate the workload of a given date as a percentage.

        Args:
            date (str): The date for which workload needs to be calculated.

        Returns:
            int: Workload percentage (rounded down).
                -1 if the date is invalid (e.g., last day of the month).
        """
        if date.split('-')[-1] == '0':
            return -1
        bookings = (Booking.objects.filter(booking_date=date)
                    .exclude(status='canceled'))
        book_time = 0
        for booking in bookings:
            start_time = booking.start_time
            end_time = booking.end_time
            start = datetime.combine(datetime.today(), start_time)
            end = datetime.combine(datetime.today(), end_time)
            duration = (end - start).seconds // 3600
            book_time += duration
        if self.is_weekend(date):
            return int((book_time / self.WEEKEND_DAY_HOURS) * 100)
        return int((book_time / self.ORDINARY_DAY_HOURS) * 100)

    def get_week_load(self, week: list) -> list:
        """
        Distribute workload across the week.

        Args:
            week (list): A list of day numbers representing the week.

        Returns:
            list: A list of tuples containing day information, workload
             percentage, and available slots.
        """
        week_load = []
        for day in week:
            date = f'{self.year}-{self.month}-{day}'
            slots = SlotsFinder(date).find_available_slots()
            day_load = (day, self.get_day_load(date), slots)
            week_load.append(day_load)
        return week_load

    def is_weekend(self, date: str) -> bool:
        """
        Check if the given date falls on a weekend.

        Args:
            date (str): The date for which to check.

        Returns:
            bool: True if the date is a weekend (Saturday or Sunday),
             False otherwise.
        """
        f_date = datetime.strptime(date, "%Y-%m-%d")
        return f_date.weekday() >= self.FRIDAY

    def get_month_load(self):
        """
        Calculate the full month's workload distribution.

        Returns:
            list: A list of weekly workload information.
        """
        return [self.get_week_load(week) for week in self.calendar]
