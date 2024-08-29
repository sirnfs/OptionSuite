import datetime
import decimal
import unittest
from base import put
from optionPrimitives import putVertical
from optionPrimitives import optionPrimitive
from parameterized import parameterized
from riskManager import putVerticalRiskManagement


class TestPutVerticalRiskManagement(unittest.TestCase):

    def setOptionsHelper(self, closeDuration: int, expirationDateTime: datetime.datetime,
                         settlementPricePutToBuy: decimal.Decimal, settlementPricePutToSell: decimal.Decimal,
                         managementType: putVerticalRiskManagement.PutVerticalManagementStrategyTypes):
        """Helper to set values for testing. """
        orderQuantity = 1
        contractMultiplier = 100
        putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                           strikePrice=decimal.Decimal(325),
                           dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                           expirationDateTime=expirationDateTime,
                           tradeDateTime=datetime.datetime.strptime('12/22/1989', "%m/%d/%Y"),
                           tradePrice=decimal.Decimal(0.5005), settlementPrice=settlementPricePutToBuy)
        putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                            strikePrice=decimal.Decimal(345),
                            dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                            expirationDateTime=expirationDateTime,
                            tradeDateTime=datetime.datetime.strptime('12/22/1989', "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(1.125), settlementPrice=settlementPricePutToSell)
        self.__shortPutVertical = putVertical.PutVertical(orderQuantity, contractMultiplier, putToBuy, putToSell,
                                                          optionPrimitive.TransactionType.SELL)

        # Set up risk management strategy. The first argument doesn't matter if closeDuration is set.
        self.__riskManagementObj = putVerticalRiskManagement.PutVerticalRiskManagement(managementType=managementType,
                                                                                       closeDuration=closeDuration)

    @parameterized.expand([
        ("CloseDurationNumberOfDays", 3, datetime.datetime.strptime('01/05/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125), None),
        ("CloseDurationPercentage", 0, datetime.datetime.strptime('01/05/1990', "%m/%d/%Y"),
         decimal.Decimal(0.7), decimal.Decimal(0.7), None),
        ("CloseDurationPercentageBackup", 0, datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125), None),
        ("HoldToExpiration", None, datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.HOLD_TO_EXPIRATION),
        ("CloseAt50Percent", None, datetime.datetime.strptime('01/05/1990', "%m/%d/%Y"),
         decimal.Decimal(0.7), decimal.Decimal(0.7),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT),
        ("CloseAt50PercentBackup", None, datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT),
        ("CloseAt50PercentOr21Days50Percent", None,
         datetime.datetime.strptime('01/05/1990', "%m/%d/%Y"),
         decimal.Decimal(0.7), decimal.Decimal(0.7),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS),
        ("CloseAt50PercentOr21Days21Days", None,
         datetime.datetime.strptime('01/23/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS),
        ("CloseAt50PercentOr21DaysBackup", None,
         datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS),
        ("CloseAt50PercentOr21DaysOrHalfLoss21Days", None,
         datetime.datetime.strptime('01/23/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS),
        ("CloseAt50PercentOr21DaysOrHalfLossGreaterThan50Percent", None,
         datetime.datetime.strptime('01/05/1990', "%m/%d/%Y"),
         decimal.Decimal(0.7), decimal.Decimal(0.7),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS),
        ("CloseAt50PercentOr21DaysOrHalfLossLessThan50Percent", None,
         datetime.datetime.strptime('01/05/1990', "%m/%d/%Y"),
         decimal.Decimal(0.4), decimal.Decimal(2.0),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS),
        ("CloseAt50PercentOr21DaysOrHalfLossBackup", None,
         datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_50_PERCENT_OR_21_DAYS_OR_HALFLOSS),
        ("CloseAt21Days", None,
         datetime.datetime.strptime('01/23/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_21_DAYS),
        ("CloseAt21DaysBackup", None,
         datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125),
         putVerticalRiskManagement.PutVerticalManagementStrategyTypes.CLOSE_AT_21_DAYS),
        ("InvalidManagementStrategy", None,
         datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
         decimal.Decimal(0.5005), decimal.Decimal(1.125),
         None),
    ])
    def testManagePosition(self, name, closeDuration, expirationDateTime, settlementPricePutToBuy,
                           settlementPricePutToSell, managementType):
        """Tests all cases for managePosition."""
        self.setOptionsHelper(closeDuration, expirationDateTime, settlementPricePutToBuy, settlementPricePutToSell,
                              managementType)
        if not name == 'InvalidManagementStrategy':
            self.assertTrue(self.__riskManagementObj.managePosition(self.__shortPutVertical))
        else:
            with self.assertRaisesRegex(
                NotImplementedError,
                    'No management strategy was specified or has not yet been implemented.'):
                self.__riskManagementObj.managePosition(self.__shortPutVertical)
        print('Test %s passed.' % name)


if __name__ == '__main__':
    unittest.main()
