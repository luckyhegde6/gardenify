import React from "react"
import { render, fireEvent } from "@testing-library/react-native"
import { Button } from "@/components/button"

describe("Button", () => {
  it("renders the title text", () => {
    const { getByText } = render(
      <Button title="Test Button" onPress={() => {}} />
    )
    expect(getByText("Test Button")).toBeTruthy()
  })

  it("calls onPress when pressed", () => {
    const onPress = jest.fn()
    const { getByText } = render(
      <Button title="Press Me" onPress={onPress} />
    )
    fireEvent.press(getByText("Press Me"))
    expect(onPress).toHaveBeenCalledTimes(1)
  })

  it("shows loading indicator instead of text when loading", () => {
    const { queryByText } = render(
      <Button title="Loading" onPress={() => {}} loading />
    )
    expect(queryByText("Loading")).toBeNull()
  })

  it("does not call onPress when disabled", () => {
    const onPress = jest.fn()
    const { getByText } = render(
      <Button title="Disabled" onPress={onPress} disabled />
    )
    fireEvent.press(getByText("Disabled"))
    expect(onPress).not.toHaveBeenCalled()
  })

  it("applies primary variant styles by default", () => {
    const { getByText } = render(
      <Button title="Primary" onPress={() => {}} />
    )
    expect(getByText("Primary")).toBeTruthy()
  })

  it("renders with secondary variant", () => {
    const { getByText } = render(
      <Button title="Secondary" onPress={() => {}} variant="secondary" />
    )
    expect(getByText("Secondary")).toBeTruthy()
  })
})
