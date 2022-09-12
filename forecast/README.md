Referenced links
1. Secrets: https://github.com/Azure/actions-workflow-samples/blob/master/assets/create-secrets-for-GitHub-workflows.md
2. Coingecko Doc: https://www.coingecko.com/en/api/documentation https://github.com/man-c/pycoingecko
3. Machine learning mastery:
    - https://machinelearningmastery.com/time-series-forecasting-methods-in-python-cheat-sheet/
    - https://machinelearningmastery.com/convert-time-series-supervised-learning-problem-python/
    - https://machinelearningmastery.com/time-series-prediction-lstm-recurrent-neural-networks-python-keras/
4. PyGithub
    - https://pygithub.readthedocs.io/en/latest/examples/Repository.html#get-a-specific-content-file
    - https://martinheinz.dev/blog/25


### ENV:

        export GH_ACCESS_TOKEN="*****************"
        export GITHUB_REPOSITORY="krishnajiraoh/my-crypto-world”
        export HISTORY_DATA_PATH="forecast/data/HistoryData.csv"
        export FORECASTED_PRICES_FILE_PATH="forecast/data/ForecastedPrices.csv"
        export MONITORING_FILE_PATH="forecast/data/Monitoring.csv"
        export ACTUALVSFORECASTED_FILEPATH="forecast/data/ActualVsForecasted.csv"
        export COIN=“bitcoin” 
        export LOOK_BACK_DAYS=30 