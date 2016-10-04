import lx

# Querring and Adding User Values

def query_User_Value(self, index, argPrefix, argName):
    if not self.dyna_IsSet(index):
        return lx.eval('user.value %s ?' % (argPrefix + argName))


def query_User_Values(self, argPrefix):
    userValues = []

    for i in xrange(0, self.attr_Count()):
        userValues.append(query_User_Value(self, i, argPrefix, self.attr_Name(i)))

    return userValues


def add_User_Values(self, userValues):
    for i in xrange(0, len(userValues)):
        self.dyna_Add(userValues[i][0], userValues[i][1])
        if userValues[i][2]:
            self.basic_SetFlags(i, lx.symbol.fCMDARG_OPTIONAL)
