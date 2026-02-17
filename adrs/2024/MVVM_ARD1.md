# Title
LiveData for a Currency conversion functions

## Context
What is the issue that we're seeing that is motivating this decision or change?
-Currency conversion functions are very important for many applications nowadays because one application might have users from various nationalities, and handling this function well is crucial.

## Decision
What is the solution that we're proposing and/or doing?
-We chose MVVM as our application architecture for managing the state related to currencies.

## Rationale
Why do we choose this solution?
-We chose MVVM because separating the view from the logic makes it possible to have different teams work on different components simultaneously. This allows us to focus on each part more easily. For example, if we want to focus on setting the data for exchanging currency, we will primarily focus on the ViewModel part.

## Consequences
Pros – What becomes easier?
-The division of the different parts of the application makes the code easier to understand.
-LiveData ensures that the UI stays up to date with the latest data and is lifecycle-aware, preventing memory leaks and crashes due to accessing stale data.


Cons – What becomes more difficult?
-By the complex data binding, the debugging in ViewModel was very hard to handle and the code was very complicated to fix.

## Sample code
Give some sample code related to this decision.

*Java

class CurrenciesViewModel : ViewModel() {

    //immutable to observe in the view
    val currencies: LiveData<State<List<Currency>>> get() = _currencies
    private val _currencies = MutableLiveData<State<List<Currency>>>()
    
    //the current select currency
    val selectedCurrency: Currency? get() = _selectedCurrency
    private var _selectedCurrency: Currency? = null
    
    //function to load all the currencies
    fun loadCurrencies() {
    
        _currencies.value = State.loading()
        
        viewModelScope.launch {
            val state = withContext(Dispatchers.Default) {
                try {
                    val currenciesValue = useCase.getAllCurrencies()
                    State.success(currenciesValue)
                } catch (exception: Exception) {
                    State.error(exception.message)
                }
            }
            _currencies.value = state
        }
    }
    
    //this will be invoked when currency is selected from dropdown
    fun changeSelectedCurrency(selectedCurrency: Currency) {
        _selectedCurrency = selectedCurrency
    }
    ...
}

  *This section is dedicated to the ViewModel responsible for managing state related to currencies. This ViewModel is responsible for managing the state related to currencies, loading them asynchronously using coroutines, and updating the UI through LiveData objects. The separation of concerns is maintained with clear responsibilities for each function within the ViewModel.