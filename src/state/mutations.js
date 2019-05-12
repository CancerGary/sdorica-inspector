export const toastMsg = (state, payload) => {
  state.snackbarMessage = payload;
  state.snackbarState = true;
}

export const setToastState = (state, payload) => {
  state.snackbarState = payload;
}

export const updateConvertRule = (state, payload) => {
  state.convertRule = payload
}

export const setLoading = (state, payload) => {
  state.onLoading = payload
}