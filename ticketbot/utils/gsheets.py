import time
import gspread
import asyncio
import aiosqlite

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.sql import text
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from pathlib import Path

from ticketbot.services import SheetRepository

file_path = Path(__file__).parent  # Debug
# db = connect(':memory:', check_same_thread=False)
# db.execute('CREATE TABLE IF NOT EXISTS sheet (cell STR, color STR, value STR, worker STR, date INT)')
# db.commit()

users = {'0, 1, 0': 'Зеленый (Лозицкий)',
         '1, 1, 0': 'Желтый (Кожиков)',
         '1, 0, 1': 'Лиловый (Кондратьев)',
         '0.9843137, 0.7372549, 0.015686275': 'Грязно-оранжевый(Савченков)',
         '1, 0, 0': 'Красный (Выходной)',
         '1, 1, 1': 'Белый(не утверждено)',
         '0': 'Не известно'}


class GoogleSheetTracker:
    def __init__(
        self,
        session: AsyncSession,
        service_account: str = 'service_account.json',
        sheet_name: str = 'scitelswork',
    ):
        """
        :param service_account: json key file path for google service account
        :param sheet_name: name of google sheet
        """
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_file(service_account, scopes=scopes)
        # credentials = ServiceAccountCredentials.from_json_keyfile_name(service_account, scope)
        self.client = gspread.authorize(credentials)
        self.spreadsheet = self.client.open(sheet_name)
        self.worksheet = self.spreadsheet.sheet1
        self.service = build('sheets', 'v4', credentials=credentials)
        self.sheet_id = self.spreadsheet.id
        self.sheet_idrange_name = f"{self.worksheet.title}!UB4:ABD154"
        self.db = session


    def get_cell_address(self, row_idx, col_idx):
        col_str = ''
        while col_idx > 0:
            col_idx -= 1
            col_str = chr(ord('A') + col_idx % 26) + col_str
            col_idx //= 26
        return f"{self.worksheet.title}!{col_str}{row_idx}"

    def find_data(self, cell: str, data):
        for elem in data:
            if elem[0] == cell:
                return elem

    async def track_changes(self):
        result = []
        num_requests = 0
        values = self.service.spreadsheets().values().get(spreadsheetId=self.sheet_id, range=self.sheet_idrange_name).execute().get('values', [])
        db_data = await self.db.execute(text('SELECT * FROM sheet'))
        db_data = db_data.fetchall()

        for row_idx, row in enumerate(values, start=4):
            for col_idx, cell_value in enumerate(row, start=548):
                request = self.find_data(f'{row_idx}, {col_idx}', db_data)
                if request is None:
                    request = [f'{row_idx}, {col_idx}', '0', None, int(time.time()), 'Не известно']
                if not (request[2] is None and cell_value == '') and request[2] != cell_value and num_requests < 59:
                    num_requests += 1
                    print('Request: ', num_requests)
                    cell_data = self.service.spreadsheets().get(spreadsheetId=self.sheet_id, ranges=self.get_cell_address(row_idx, col_idx), includeGridData=True).execute()
                    cell = cell_data['sheets'][0]['data'][0]['rowData'][0]['values'][0]
                    color = ', '.join(str(cell['effectiveFormat']['backgroundColor'].get(key, 0)) for key in ['red', 'green', 'blue'])
                    worker = await SheetRepository(self.db).get_user_fcolor(color)
                    if worker is None:
                        worker = 'Не известно'
                    else:
                        worker = f'{worker.color.name}({worker.first_name})'
                    new_cell = {'cell': f'{row_idx}, {col_idx}', 'color': color, 'worker': worker, 'value': cell_value, 'date': int(time.time())}
                    old_cell = {'cell': request[0], 'color': request[1], 'value': request[2], 'worker': request[4], 'date': request[3]}
                    result.append({'old': old_cell, 'new': new_cell})
                    await self.db.execute(text('UPDATE sheet SET color = :1, value = :2, worker = :3, date = :4 WHERE cell = :5'), {'1': color, '2': cell_value, '4': int(time.time()), '3': worker, '5': f'{row_idx}, {col_idx}'})
                if num_requests >= 59:
                    print(f'Requests: {num_requests}, sleeping')
                    await asyncio.sleep(60)
                    num_requests = 0

        await self.db.commit()
        return result

    async def debug(self, db_path: str = 'debug.db'):  # Полное обновление значений ячеек в бд без цвета
        values = self.service.spreadsheets().values().get(spreadsheetId=self.sheet_id, range=self.sheet_idrange_name).execute().get('values', [])
        await self.db.execute('DELETE FROM sheet')
        for row_idx, row in enumerate(values, start=4):
            for col_idx, cell_value in enumerate(row, start=548):
                await self.db.execute('INSERT INTO sheet VALUES (?, ?, ?, ?, ?)', (f"{row_idx}, {col_idx}", '0', cell_value, 'Не известно', int(time.time()),))
        await self.db.commit()

