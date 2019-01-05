export const toastMsg = (state, payload) => {
  state.snackbarMessage = payload;
  state.snackbarState = true;
}

export const setToastState = (state, payload) => {
  state.snackbarState = payload;
}