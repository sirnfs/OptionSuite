import datetime
import decimal
import unittest
from base import call
from base import put
from optionPrimitives import strangle
from optionPrimitives import optionPrimitive
from parameterized import parameterized
from riskManager import strangleRiskManagement


class TestStrangleRiskManagement(unittest.TestCase):

    def setOptionsHelper(self, expirationDateTime: datetime.datetime, settlementPricePut: decimal.Decimal,
                         settlementPriceCall: decimal.Decimal,
                         managementType: strangleRiskManagement.StrangleManagementStrategyTypes):
        """Helper to set values for testing. """
        orderQuantity = 1
        contractMultiplier = 100
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690), delta=0.15, vega=0.04, theta=-0.07, gamma=0.11,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=expirationDateTime,
                         tradePrice=decimal.Decimal(7.475), settlementPrice=settlementPricePut)
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855), delta=-0.16, vega=0.05, theta=-0.06, gamma=0.12,
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=expirationDateTime,
                            tradePrice=decimal.Decimal(5.30), settlementPrice=settlementPriceCall)
        self.__strangleObj = strangle.Strangle(orderQuantity=orderQuantity, contractMultiplier=contractMultiplier,
                                               callOpt=callOpt, putOpt=putOpt,
                                               buyOrSell=optionPrimitive.TransactionType.SELL)

        # Set up risk management strategy. The first argument doesn't matter if closeDuration is set.
        self.__riskManagementObj = strangleRiskManagement.StrangleRiskManagement(managementType=managementType)

    @parameterized.expand([
        ("HoldToExpiration", datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
         decimal.Decimal(7.475), decimal.Decimal(5.30),
         strangleRiskManagement.StrangleManagementStrategyTypes.HOLD_TO_EXPIRATION),
        ("CloseAt50Percent", datetime.datetime.strptime('01/03/2021', "%m/%d/%Y"),
         decimal.Decimal(2.0), decimal.Decimal(2.0),
         strangleRiskManagement.StrangleManagementStrategyTypes.CLOSE_AT_50_PERCENT),
        ("CloseAt50PercentBackup", datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
         decimal.Decimal(7.475), decimal.Decimal(5.30),
         strangleRiskManagement.StrangleManagementStrategyTypes.CLOSE_AT_50_PERCENT),
        ("CloseAt50PercentOr21Days50Percent",
         datetime.datetime.strptime('01/03/2021', "%m/%d/%Y"),
         decimal.Decimal(2.0), decimal.Decimal(2.0),
         strangleRiskManagement.StrangleManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS),
        ("CloseAt50PercentOr21Days21Days",
         datetime.datetime.strptime('01/22/2021', "%m/%d/%Y"),
         decimal.Decimal(7.475), decimal.Decimal(5.30),
         strangleRiskManagement.StrangleManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS),
        ("CloseAt50PercentOr21DaysBackup",
         datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
         decimal.Decimal(7.475), decimal.Decimal(5.30),
         strangleRiskManagement.StrangleManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS),
        ("InvalidManagementStrategy",
         datetime.datetime.strptime('01/03/2021', "%m/%d/%Y"),
         decimal.Decimal(7.475), decimal.Decimal(5.30),
         None),
    ])
    def testManagePosition(self, name, expirationDateTime, settlementPricePut, settlementPriceCall, managementType):
        """Tests all cases for managePosition."""
        self.setOptionsHelper(expirationDateTime, settlementPricePut, settlementPriceCall, managementType)
        if not name == 'InvalidManagementStrategy':
            self.assertTrue(self.__riskManagementObj.managePosition(self.__strangleObj))
        else:
            with self.assertRaisesRegex(
                NotImplementedError,
                    'No management strategy was specified or has not yet been implemented.'):
                self.__riskManagementObj.managePosition(self.__strangleObj)
        print('Test %s passed.' % name)


if __name__ == '__main__':
    unittest.main()
