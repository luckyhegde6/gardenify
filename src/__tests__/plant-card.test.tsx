import React from "react"
import { render, fireEvent } from "@testing-library/react-native"
import { PlantCard } from "@/components/plant-card"

describe("PlantCard", () => {
  const defaultProps = {
    scientificName: "Rosa damascena",
    commonNames: ["Damask Rose", "Rose"],
    confidence: 0.95,
  }

  it("renders common name", () => {
    const { getByText } = render(<PlantCard {...defaultProps} />)
    expect(getByText("Damask Rose")).toBeTruthy()
  })

  it("renders scientific name", () => {
    const { getByText } = render(<PlantCard {...defaultProps} />)
    expect(getByText("Rosa damascena")).toBeTruthy()
  })

  it("shows confidence percentage", () => {
    const { getByText } = render(<PlantCard {...defaultProps} />)
    expect(getByText("95.0%")).toBeTruthy()
  })

  it("handles low confidence scores", () => {
    const { getByText } = render(
      <PlantCard {...defaultProps} confidence={0.35} />
    )
    expect(getByText("35.0%")).toBeTruthy()
  })

  it("uses scientific name as display when no common names", () => {
    const { getAllByText } = render(
      <PlantCard
        scientificName="Rosa canina"
        commonNames={[]}
        confidence={0.8}
      />
    )
    const matches = getAllByText("Rosa canina")
    expect(matches.length).toBe(2)
  })

  it("calls onPress when pressed", () => {
    const onPress = jest.fn()
    const { getByText } = render(
      <PlantCard {...defaultProps} onPress={onPress} />
    )
    fireEvent.press(getByText("Damask Rose"))
    expect(onPress).toHaveBeenCalledTimes(1)
  })
})
