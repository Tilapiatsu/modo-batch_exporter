import lx
import Tila_BatchExportModule as t

# Querring and Adding User Values

def query_User_Value(self, index, argPrefix, argName):
    if not self.dyna_IsSet(index) and argName != t.TILA_PRESET_NAME:
        return lx.eval('user.value %s ?' % (argPrefix + argName))
    else:
        if t.userValues[index][1] == 'boolean':
            return self.dyna_Bool(index)
        if t.userValues[index][1] == 'float':
            return self.dyna_Float(index)
        if t.userValues[index][1] == 'integer':
            return self.dyna_Int(index)
        if t.userValues[index][1] == 'string':
            return self.dyna_String(index)


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
