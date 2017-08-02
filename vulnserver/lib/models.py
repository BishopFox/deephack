import string
import random
import sys
import os
from IPython.core import ultratb
if bool(os.environ.get('VULNSERVER_DEBUG')) == True:
    sys.excepthook = ultratb.FormattedTB(mode='Verbose',
         color_scheme='Linux', call_pdb=1)

from faker import Faker

from sqlalchemy import *
from sqlalchemy import Column, Integer, String, Date,Table, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

#hack please ignore
db_type = os.environ.get('VULNSERVER_DB_TYPE', '')
engine = None
if db_type.lower() == 'postgres':
    print("starting postgres server")
    engine = create_engine('postgresql+psycopg2://deephack:deephack@/deephack?host=/var/run/postgresql/')
else:
    engine = create_engine('sqlite:///:memory:')
Base = declarative_base()
Fake = Faker()

'''
TODO
    - set column names to mined column names
    - set table names to mined table names

    - scraping ideas
        - search github.com for all .sql files
            - parse them for create table statements
            - use those to populate table names
'''

'''
    patterns - column names
    {keyword}_{randint}
    {keyword}_id
    {product_prefix}_{keyword}
    {small_az_code}_{keyword}
    {product_prefix}_{keyword}_{randint}
    {small_az_code}_{keyword}_{randint}
    {product_prefix}_{keyword}{randint}
    {small_az_code}_{keyword}{randint}
    {keyword}
    {keyword}_{keyword}
    {keyword}_{keyword}_{keyword}
    {keyword}_{keyword}_{keyword}_{keyword}

    table names
    {keyword}
    {product_prefix}_keyword
    {product_prefix}Keyword
    {keyword}{int}
    {product_prefix}_keyword{int}
    {product_prefix}Keyword{int}
    {keyword}_{int}
    {product_prefix}_keyword_{int}
    {product_prefix}Keyword_{int}
'''

class NamePatterns:
    '''Class for generating random realistic name patterns'''
    # TODO: finish name pattern functions
    def __init__(self):
        self.name_patterns = {
            "keyword_randint": self.keyword_randint,
            #"keyword_id": self.keyword_id,
            "product_keyword": self.product_keyword,
            #"small_code_keyword": self.small_code_keyword,
            #"product_prefix_keyword_randint": self.product_prefix_keyword_randint,
            #"small_code_keyword_randint": self.small_code_keyword_randint,
            #"product_keywordrandint": self.product_keywordrandint,
            #"small_code_keywordrandint": self.small_code_keywordrandint,
            "keyword": self.keyword,
            "keyword_skeyword": self.keyword_skeyword,
            "keyword_skeyword_skeyword": self.keyword_skeyword_skeyword,
            "keyword_skeyword_skeyword_skeyword": self.keyword_skeyword_skeyword_skeyword,
        }

        self.product_code = "".join([random.choice(string.ascii_letters) for i in range(
            0, random.randint(1,5))])
        self.table_secondary_keywords = self.get_table_secondary_keywords()

    def _get_secondary_keyword(self):
        return 'test_secondary'

    def _get_product(self):
        return 'test_product'

    def _get_small_code(self):
        return 'test_product'

    def _get_randint(self):
        return random.choice(['00', '01', '02', '03','0', '1', '2', '3'])

    def _camelcase(self, argv):
        '''camel cases the first letter of each word in keywords list'''
        camel_cased=[]
        for i in argv:
            first_letter = i[:1].upper()
            camel_cased.append(first_letter+i[1:])
        return "".join(camel_cased)

    def _underscores(self, argv):
        '''adds unscores to keywords'''
        return "_".join(["{"+str(i)+"}" for i in range(len(argv))]).format(*argv)

    def _nospaces(self, argv):
        '''adds unscores to keywords'''
        return "".join(["{"+str(i)+"}" for i in range(len(argv))]).format(*argv)

    def _random_fmt(self, argv):
        ''' return a format string with a specified number of args,
        either camel case, underscores, or nospaces'''
        selector = random.choice(['camelcase','underscores','nospaces'])
        selectors = {
            'underscores': self._underscores,
            'nospaces': self._nospaces,
            #'camelcase': self._camelcase,
        }
        return selectors.get(selector, self._underscores)(argv)

    def original_column_name(self, column_name):
        return column_name

    def keyword_randint(self, column_name):
        randint = self._get_randint()
        return self._random_fmt([column_name, randint])

    def keyword_id(self, column_name):
        pass

    def product_keyword(self, column_name):
        return self._random_fmt([self.product_code, column_name])

    def small_code_keyword(self, column_name):
        pass

    def product_keyword_randint(self, column_name):
        pass

    def small_code_keyword_randint(self, column_name):
        pass

    def product_keywordrandint(self, column_name):
        pass

    def small_code_keywordrandint(self, column_name):
        pass

    def keyword(self, column_name):
        return column_name

    def keyword_skeyword(self, column_name):
        return self._random_fmt([column_name,
            random.choice(self.table_secondary_keywords)])

    def keyword_skeyword_skeyword(self, column_name):
        return self._random_fmt([column_name,
            random.choice(self.table_secondary_keywords),
            random.choice(self.table_secondary_keywords),
            ])

    def keyword_skeyword_skeyword_skeyword(self, column_name):
        return self._random_fmt([column_name,
            random.choice(self.table_secondary_keywords),
            random.choice(self.table_secondary_keywords),
            random.choice(self.table_secondary_keywords),
            ])

    def get_table_secondary_keywords(self):
        cur_path = os.path.dirname(os.path.abspath(__file__))
        keyword_path = os.path.join(cur_path, 'keywords')
        if not os.path.is_file(keyword_path):
            sys.exit("need text file with keywords to generate table and column names")
        with open(keyword_path) as f:
             return [i.strip() for i in f.readlines()]

    def get_name(self, name_opts):
        '''generate a random name pattern from list name_opts'''
        # choose item from provided list
        name_opt = random.choice(name_opts)
        # choose a random pattern func
        pattern_choice = self.name_patterns[
                random.choice(list(
                    self.name_patterns.keys()))]
        # populate the pattern and return
        return pattern_choice(name_opt).lower()

class User:
    '''Generate a user table'''
    def get_tables(self, num_tables=1):
        tables = {}
        for i in range(num_tables):
            table_name = self.get_table_keyword()
            # loop until we generate a unique tablename
            while table_name.lower() in [x.lower() for x in tables.keys()]:
                table_name = self.get_table_keyword()
            #print("creating table name: %s" % table_name)
            columns = self.create_table(table_name)
            #print("columns %s" % columns)
            tables[table_name] = columns
        print("creating table %s" % tables)
        return tables

    def get_table_keyword(self):
        np = NamePatterns()
        return np.get_name([
            'users','usrs','user', 'usr',
            'groups','grps','group', 'grp',
            'customers','customer','cstmr', 'cst',
            'product','product','inventory', 'invt',
            'admin','administrator','manage', 'superuser',
            'account','acct','archive', 'message', 'msg',
            'vote','core','article', 'post',
            ])

    def _get_sqlalchemy_type(self, cname, primary_key=False, relationship=None):
        ''' returns a random sqlalchemy type, return str for now '''
        if primary_key:
            return Column(cname, Integer, primary_key=True, autoincrement=True)
        else:
            return Column(cname, String)

    def create_table(self, table_name, num_columns=5):

        faker_types = {
            Fake.user_name: ['user', 'usr',
                'uname', 'usrnme','username', 'user_name'],
            Fake.email: ['email', 'emailaddr', 'email_addr', 'emailaddress','mailaddr','contactemail','contact_email'],
            Fake.company_email: ['email', 'emailaddr', 'email_addr', 'emailaddress','mailaddr','contactemail','contact_email'],
            Fake.password: ['password', 'passwd', 'pword', 'pw','password_hash', 'passwd_hash', 'pword_hash', 'pw_hash'],
            Fake.address: ['addr', 'address', 'location', 'mailing_addr', 'mail_addr', 'mailing_address'],
            Fake.phone_number: ['phone_number', 'pnumber', 'phonenum', 'phone', 'cell', 'cellphone', 'contact_number', 'contact_num'],
            Fake.company: ['company', 'business'],
            Fake.credit_card_full: ['cc_details', 'card_data', 'creditcard', 'credit_card', 'cc'],
            #Fake.credit_card_provider,
            Fake.md5: ['password', 'passwd', 'pword', 'pw','password_hash', 'passwd_hash', 'pword_hash', 'pw_hash'],
            Fake.sha1: ['password', 'passwd', 'pword', 'pw','password_hash', 'passwd_hash', 'pword_hash', 'pw_hash'],
            Fake.sha256: ['password', 'passwd', 'pword', 'pw','password_hash', 'passwd_hash', 'pword_hash', 'pw_hash'],
            Fake.bs: ['information', 'info', 'story', 'content', 'post', 'blogtext', 'text'],
            #Fake.boolean,
            #Fake.chrome,
            #Fake.paragraph,
            #Fake.ipv4,
            #Fake.uuid4,
        }

        columns = {}
        col_patterns = NamePatterns()

        # get column names
        for i in range(0, num_columns):
            # get a random Faker data type
            faker_type = random.choice(list(faker_types.keys()))
            # get a random column_name
            column_name = col_patterns.get_name(faker_types[faker_type])
            # get a random sqlalchemy type
            sqla_type = self._get_sqlalchemy_type(column_name)
            # add a hook for the random_data function so we know
            # what kind of random data to generate
            sqla_type.faker_type = faker_type
            columns[column_name] = sqla_type

        # add primary key
        columns[table_name + '_id'] = self._get_sqlalchemy_type(
                table_name + '_id', primary_key=True)
        return columns

class SchemaGen():
    def __init__(self):
        self.db_identifiers = string.ascii_letters# + '-_@#'
        self.db_value_fuzz = 5893
        self.db_value_max = 100000 + random.randrange(0, self.db_value_fuzz)
        self.table_max = self.db_value_max * .03
        self.table_fuzz = 500
        self.table_name_max = 75
        self.column_max = self.db_value_max * .07
        self.column_fuzz = 500
        self.column_name_max = 75
        self.columns_per_table_max = 75
        self.columns_per_table_min = 2

    def get_identifier_names(self, imax, ifuzz, iname_max):
        names = []
        # get a random value for the identifier range
        irange = imax + random.randrange(0, ifuzz)
        while irange > 0:
            name = ''
            for i in range(random.randrange(3, iname_max)):
                name = name + self.db_identifiers[random.randint(0,len(self.db_identifiers))-1]
                irange = irange - 1
            names.append(''+name+'')
        return names

    def gen_tdict(self):
        '''
        create the table dict with all columns and define
        python classes for each table. each class inherits from
        sqlalchemy Base and can be instantiated with sqlalchemy
        [tnames]
        [cnames]
        tables = {"table_name": {column_name:random_type,
                                    column_name:random_type,
                                    column_name:random_type,
                                    column_name:random_relationship}}
        '''
        tnames = self.get_identifier_names(
                    self.table_max,
                    self.table_fuzz,
                    self.table_name_max)
        cnames = self.get_identifier_names(
                    self.column_max,
                    self.column_fuzz,
                    self.column_name_max)
        tdict = {}
        while len(tnames) > 0 and len(cnames) >= self.columns_per_table_min:
            columns = {}
            tname = tnames.pop()
            self.db_value_max = self.db_value_max - len(tname)
            for i in range(random.randrange(
                    self.columns_per_table_min,
                    self.columns_per_table_max)):
                if len(cnames) > 0:
                    cname = cnames.pop()
                    columns[cname] = self._get_sqlalchemy_type(cname) if i > 0 else self._get_sqlalchemy_type(cname, primary_key=True)
                    # choose random faker_type for column
                    self.db_value_max = self.db_value_max - len(cname)
            tdict[tname] = columns
        self.tdict = tdict
        return self.tdict

    def gen(self):
        self.gen_tdict()
        for k,v in self.tdict.items():
            v['__tablename__'] = k
            type(k, (Base, ), v)

    def _get_sqlalchemy_type(self, cname, primary_key=False, relationship=None):
        ''' returns a random sqlalchemy type, return str for now '''
        if primary_key:
            return Column(cname, Integer, primary_key=True, autoincrement=True)
        else:
            return Column(cname, String)

    def _create_database(self):
        db_name = 'deephack'
        conn = engine.connect()
        Base.metadata.create_all(engine)
        metadata = Base.metadata

        while self.db_value_max > 0:
            tables = [i for i in metadata.tables]
            cur_table = tables[random.randrange(0,
                len(tables)-1)]
            cur_table = metadata.tables[cur_table]
            # add 50 rows
            rows = []
            for i in range(3):
                row_dict = {}
                for column in cur_table.columns:
                    if not column.primary_key:
                        row_dict[str(column.name)] = self.random_data()
                rows.append(row_dict)
            conn.execute(cur_table.insert(), rows)
            self.db_value_max = self.db_value_max - 500
        conn.close()

    def populate(self):
        ''' populate the database '''
        self._create_database()

    def select_table(self):
        '''returns the table to use for selects for this episode,
        only call this once per episode'''
        tables = [i for i in Base.metadata.tables]
        self.cur_table = Base.metadata.tables[random.choice(tables)]
        self.pk = [i for i in self.cur_table.primary_key.columns][0]
        return (self.cur_table, self.pk)

    def random_data(self):
        rc = []
        for x in range(random.randrange(0,200)):
            rc.append(string.printable[random.randrange(len(string.printable)-1)])
        return "".join(rc)

    def get_engine(self):
        return engine


class FakerSchema(SchemaGen):
    '''uses faker to generate a table of all fake data'''

    def gen_tdict(self):
        user = User()
        self.tdict = user.get_tables()

    def _create_database(self):
        db_name = 'deephack'
        conn = engine.connect()
        Base.metadata.create_all(engine)
        self.metadata = Base.metadata

        while self.db_value_max > 0:
            tables = [i for i in self.metadata.tables]
            cur_table = random.choice(tables)
            cur_table = self.metadata.tables[cur_table]
            # add 50 rows
            rows = []
            for i in range(3):
                row_dict = {}
                for column in cur_table.columns:
                    # add faker_type to column if not exists
                    if not column.primary_key:
                        row_dict[str(column.name)] = self.random_data(column.faker_type)
                rows.append(row_dict)
            conn.execute(cur_table.insert(), rows)
            self.db_value_max = self.db_value_max - 500
        conn.close()

    def random_data(self, faker_func):
        ''' create some random data based on the faker
        type and return it'''
        if faker_func == Fake.user_name:
            return faker_func()
        else:
            return faker_func()
