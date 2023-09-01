import yaml

def init_vocab():
    return {'<PAD>': 0, '<UNK>': 1, '<START>': 2, '<END>': 3}


def invert_dict(d):
    return {v: k for k, v in d.items()}

def write_config(config, path):
    with open(path, 'w') as f:
        yaml.dump(config, f, allow_unicode=True)
        
class ValueClass():
    def __init__(self, type, value, unit=None):
        """
        When type is
            - string, value is a str
            - quantity, value is a number and unit is required
            - year, value is a int
            - date, value is a date object
        """
        self.type = type
        self.value = value
        self.unit = unit

    def isTime(self):
        return self.type in {'year', 'date'}

    def can_compare(self, other):
        if self.type == 'string':
            return other.type == 'string'
        elif self.type == 'quantity':
            # NOTE: for two quantity, they can compare only when they have the same unit
            return other.type == 'quantity' and other.unit == self.unit
        else:
            # year can compare with date
            return other.type == 'year' or other.type == 'date'

    def contains(self, other):
        """
        check whether self contains other, which is different from __eq__ and the result is asymmetric
        used for conditions like whether 2001-01-01 in 2001, or whether 2001 in 2001-01-01
        """
        if self.type == 'year': # year can contain year and date
            other_value = other.value if other.type == 'year' else other.value.year
            return self.value == other_value
        elif self.type == 'date': # date can only contain date
            return other.type == 'date' and self.value == other.value
        else:
            raise Exception('not supported type: %s' % self.type)


    def __eq__(self, other):
        """
        2001 and 2001-01-01 is not equal
        """
        assert self.can_compare(other)
        return self.type == other.type and self.value == other.value

    def __lt__(self, other):
        """
        Comparison between a year and a date will convert them both to year
        """
        assert self.can_compare(other)
        if self.type == 'string':
            raise Exception('try to compare two string')
        elif self.type == 'quantity':
            return self.value < other.value
        elif self.type == 'year':
            other_value = other.value if other.type == 'year' else other.value.year
            return self.value < other_value
        elif self.type == 'date':
            if other.type == 'year':
                return self.value.year < other.value
            else:
                return self.value < other.value

    def __gt__(self, other):
        assert self.can_compare(other)
        if self.type == 'string':
            raise Exception('try to compare two string')
        elif self.type == 'quantity':
            return self.value > other.value
        elif self.type == 'year':
            other_value = other.value if other.type == 'year' else other.value.year
            return self.value > other_value
        elif self.type == 'date':
            if other.type == 'year':
                return self.value.year > other.value
            else:
                return self.value > other.value

    def __str__(self):
        if self.type == 'string':
            return self.value
        elif self.type == 'quantity':
            if self.value - int(self.value) < 1e-5:
                v = int(self.value)
            else:
                v = self.value
            return '{} {}'.format(v, self.unit) if self.unit != '1' else str(v)
        elif self.type == 'year':
            return str(self.value)
        elif self.type == 'date':
            return self.value.isoformat()
