class EDAClientBase(object):
    def list_contracts(
        self,
        contract_number=None,
        delivery_order=None,
        cage_code=None,
        duns_number=None,
    ):
        """
        Get a list of all contracts matching the given filters.
        """
        raise NotImplementedError()

    def get_contract(self, contract_number, status):
        """
        Get details for a contract.
        """
        raise NotImplementedError()


class MockEDAClient(EDAClientBase):
    def __init__(self, *args, **kwargs):
        pass

    def list_contracts(
        self,
        contract_number=None,
        delivery_order=None,
        cage_code=None,
        duns_number=None,
    ):
        return [
            {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
            },
            {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
            },
            {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
            },
        ]

    MOCK_CONTRACT_NUMBER = "DCA10096D0052"

    # TODO: It seems likely that this will have to supply CLIN data form the
    # EDA returnclinXML API call, in addition to the basic task order data
    # below. See the EDA docs.
    def get_contract(self, contract_number, status):
        if contract_number == self.MOCK_CONTRACT_NUMBER and status == "y":
            return {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
                "amount": 2000000,
            }
        else:
            return None


class EDAClient(EDAClientBase):
    def __init__(self, base_url, user_name, user_role):
        pass

    def list_contracts(
        self,
        contract_number=None,
        delivery_order=None,
        cage_code=None,
        duns_number=None,
    ):
        # TODO: Fetch the contracts CSV and transform them into dictionaries.
        # https://docs.python.org/3/library/csv.html#csv.DictReader
        raise NotImplementedError()

    def get_contract(self, contract_number, status):
        # TODO: Fetch the contract XML and transform it into a dictionary.
        # https://docs.python.org/3.7/library/xml.etree.elementtree.html
        raise NotImplementedError()
