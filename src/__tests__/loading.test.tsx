import React from "react"
import { render } from "@testing-library/react-native"
import { Loading, LoadingOverlay } from "@/components/loading"

describe("Loading", () => {
  it("renders without crashing", () => {
    const { root } = render(<Loading />)
    expect(root).toBeTruthy()
  })

  it("shows message when provided", () => {
    const { getByText } = render(<Loading message="Loading..." />)
    expect(getByText("Loading...")).toBeTruthy()
  })

  it("renders without message", () => {
    const { queryByText } = render(<Loading />)
    expect(queryByText("Loading...")).toBeNull()
  })
})

describe("LoadingOverlay", () => {
  it("renders overlay with message", () => {
    const { getByText } = render(
      <LoadingOverlay message="Processing..." />
    )
    expect(getByText("Processing...")).toBeTruthy()
  })

  it("renders overlay without message", () => {
    const { queryByText } = render(<LoadingOverlay />)
    expect(queryByText("Processing...")).toBeNull()
  })
})
