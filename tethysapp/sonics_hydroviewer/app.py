from tethys_sdk.base import TethysAppBase
from tethys_sdk.app_settings import CustomSetting

class SonicsHydroviewer(TethysAppBase):
    """
    Tethys app class for Sonics Hydroviewer.
    """

    name = 'Sonics Hydroviewer'
    description = ''
    package = 'sonics_hydroviewer'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/icon.gif'
    root_url = 'sonics-hydroviewer'
    color = '#20295C'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def custom_settings(self):
        return (
            CustomSetting(
                name='SERVER',
                type=CustomSetting.TYPE_STRING,
                description='Server DNS or IP:PORT',
                required=True,
                default='http://localhost:8080', 
            ),
            CustomSetting(
                name='DB_USER',
                type=CustomSetting.TYPE_STRING,
                description='Database user',
                required=True,
                default='postgres',
            ),
            CustomSetting(
                name='DB_PASS',
                type=CustomSetting.TYPE_STRING,
                description='Database password',
                required=True,
                default='pass',
            ),
            CustomSetting(
                name='DB_NAME',
                type=CustomSetting.TYPE_STRING,
                description='Database name',
                required=True,
                default='postgres',
            ),
            CustomSetting(
                name='FOLDER',
                type=CustomSetting.TYPE_STRING,
                description='Folder where sonics data are located',
                required=True,
                default='/home/ubuntu/data/sonics',
            ),
        )