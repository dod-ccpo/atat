import pytest

from atst.forms.request import RequestForm


class TestRequestForm:

    form_data = {
        'dod_component': 'Army and Air Force Exchange Service',
        'jedi_usage': 'cloud-ify all the things',
        'num_software_systems': '12',
        'estimated_monthly_spend': '1000000',
        'dollar_value': '42',
        'number_user_sessions': '6',
        'average_daily_traffic': '0',
        'start_date': '12/12/2012',
    }
    migration_data = {
        'jedi_migration': 'yes',
        'rationalization_software_systems': 'yes',
        'technical_support_team': 'yes',
        'organization_providing_assistance': 'in_house_staff',
        'engineering_assessment': 'yes',
        'data_transfers': 'less_than_100gb',
        'expected_completion_date': 'less_than_1_month'
    }

    def test_require_cloud_native_when_not_migrating(self):
        extra_data = { 'jedi_migration': 'no' }
        request_form = RequestForm(data={ **self.form_data, **extra_data })
        assert not request_form.validate()
        assert request_form.errors == { 'cloud_native': ['Not a valid choice'] }

    def test_require_migration_questions_when_migrating(self):
        extra_data = { 'jedi_migration': 'yes' }
        request_form = RequestForm(data={ **self.form_data, **extra_data })
        assert not request_form.validate()
        assert request_form.errors == {
            'rationalization_software_systems': ['Not a valid choice'],
            'technical_support_team': ['Not a valid choice'],
            'organization_providing_assistance': ['Not a valid choice'],
            'engineering_assessment': ['Not a valid choice'],
            'data_transfers': ['Not a valid choice'],
            'expected_completion_date': ['Not a valid choice']
        }

    def test_require_organization_when_technical_support_team(self):
        data = { **self.form_data, **self.migration_data }
        del data['organization_providing_assistance']

        request_form = RequestForm(data=data)
        assert not request_form.validate()
        assert request_form.errors == {
            'organization_providing_assistance': ['Not a valid choice'],
        }

    def test_valid_form_data(self):
        data = { **self.form_data, **self.migration_data }
        data['technical_support_team'] = 'no'
        del data['organization_providing_assistance']

        request_form = RequestForm(data=data)
        assert request_form.validate()

    def test_sessions_required_for_large_projects(self):
        data = { **self.form_data, **self.migration_data }
        data['estimated_monthly_spend'] = '9999999'
        del data['number_user_sessions']
        del data['average_daily_traffic']

        request_form = RequestForm(data=data)
        assert not request_form.validate()
        assert request_form.errors == {
            'number_user_sessions': ['This field is required.'],
            'average_daily_traffic': ['This field is required.'],
        }

    def test_sessions_not_required_invalid_monthly_spend(self):
        data = { **self.form_data, **self.migration_data }
        data['estimated_monthly_spend'] = 'foo'
        del data['number_user_sessions']
        del data['average_daily_traffic']

        request_form = RequestForm(data=data)
        assert request_form.validate()
