"use client"

import { useState, useEffect, useCallback } from 'react'
import { Button } from "@/components/ui/button"
import { DndProvider, useDrag, useDrop } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'

type Disk = number
type Tower = Disk[]
type Towers = [Tower, Tower, Tower]

const MIN_DISKS = 3
const MAX_DISKS = 5

function generateMoves(n: number, from: number, to: number, aux: number): [number, number][] {
  if (n === 1) {
    return [[from, to]]
  }
  return [
    ...generateMoves(n - 1, from, aux, to),
    [from, to],
    ...generateMoves(n - 1, aux, to, from)
  ]
}

const Disk = ({ size, towerIndex, diskIndex, totalDisks }: { size: number; towerIndex: number; diskIndex: number; totalDisks: number }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'disk',
    item: { size, fromTower: towerIndex, diskIndex },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }))

  return (
    <div
      ref={drag}
      className="h-6 rounded-full cursor-move"
      style={{
        width: `${(size / totalDisks) * 100}%`,
        backgroundColor: `hsl(${(size / totalDisks) * 360}, 70%, 50%)`,
        opacity: isDragging ? 0.5 : 1,
      }}
      role="button"
      aria-label={`Disk ${size} on Tower ${towerIndex + 1}`}
      tabIndex={0}
    />
  )
}

const Tower = ({ tower, index, onDrop, totalDisks }: { tower: Tower; index: number; onDrop: (fromTower: number, toTower: number, diskIndex: number) => void; totalDisks: number }) => {
  const [, drop] = useDrop(() => ({
    accept: 'disk',
    drop: (item: { size: number; fromTower: number; diskIndex: number }) => {
      onDrop(item.fromTower, index, item.diskIndex)
    },
    canDrop: (item: { size: number; fromTower: number; diskIndex: number }) => {
      return item.fromTower !== index
    },
  }))

  return (
    <div
      ref={drop}
      className="flex flex-col-reverse items-center justify-end w-32 h-48 bg-gray-300 rounded-lg"
      role="region"
      aria-label={`Tower ${index + 1}`}
    >
      {tower.map((disk, diskIndex) => (
        <Disk key={diskIndex} size={disk} towerIndex={index} diskIndex={diskIndex} totalDisks={totalDisks} />
      ))}
    </div>
  )
}

export default function TowersOfHanoi() {
  const [towers, setTowers] = useState<Towers>([[], [], []])
  const [optimalMoves, setOptimalMoves] = useState<[number, number][]>([])
  const [userMoves, setUserMoves] = useState<number>(0)
  const [correctMoves, setCorrectMoves] = useState<number>(0)
  const [gameOver, setGameOver] = useState<boolean>(false)
  const [accuracy, setAccuracy] = useState<number>(100)
  const [totalDisks, setTotalDisks] = useState<number>(MIN_DISKS)

  const initializeGame = useCallback(() => {
    const diskCount = Math.floor(Math.random() * (MAX_DISKS - MIN_DISKS + 1)) + MIN_DISKS
    setTotalDisks(diskCount)
    setTowers([
      Array.from({ length: diskCount }, (_, i) => diskCount - i),
      [],
      []
    ])
    setOptimalMoves(generateMoves(diskCount, 0, 2, 1))
    setUserMoves(0)
    setCorrectMoves(0)
    setGameOver(false)
    setAccuracy(100)
  }, [])

  useEffect(() => {
    initializeGame()
  }, [initializeGame])

  const getSuggestedMove = useCallback((currentTowers: Towers, moveIndex: number): [number, number] | null => {
    const move = optimalMoves[moveIndex]
    if (!move) return null

    const [fromTower, toTower] = move
    if (currentTowers[fromTower].length === 0) {
      // If the suggested source tower is empty, find the next valid move
      for (let i = moveIndex + 1; i < optimalMoves.length; i++) {
        const [nextFrom, nextTo] = optimalMoves[i]
        if (currentTowers[nextFrom].length > 0) {
          return [nextFrom, nextTo]
        }
      }
      return null // No valid moves found
    }
    return move
  }, [optimalMoves])

  const handleDrop = (fromTower: number, toTower: number, diskIndex: number) => {
    if (fromTower === toTower) return

    setTowers(prevTowers => {
      const newTowers = prevTowers.map(tower => [...tower]) as Towers
      const diskToMove = newTowers[fromTower][diskIndex]
      newTowers[fromTower].splice(diskIndex, 1)
      newTowers[toTower].push(diskToMove)

      const suggestedMove = getSuggestedMove(prevTowers, userMoves)
      const isCorrectMove = suggestedMove && fromTower === suggestedMove[0] && toTower === suggestedMove[1]

      setUserMoves(prevMoves => prevMoves + 1)
      setCorrectMoves(prevCorrectMoves => isCorrectMove ? prevCorrectMoves + 1 : prevCorrectMoves)
      setAccuracy(prevAccuracy => {
        const newAccuracy = ((correctMoves + (isCorrectMove ? 1 : 0)) / (userMoves + 1)) * 100
        return Number(newAccuracy.toFixed(2))
      })

      if (newTowers[2].length === totalDisks) {
        setGameOver(true)
      }

      return newTowers
    })
  }

  const suggestedMove = getSuggestedMove(towers, userMoves)

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
        <h1 className="text-3xl font-bold mb-4">Towers of Hanoi</h1>
        <div className="flex justify-center space-x-8 mb-8">
          {towers.map((tower, index) => (
            <Tower key={index} tower={tower} index={index} onDrop={handleDrop} totalDisks={totalDisks} />
          ))}
        </div>
        <div className="text-lg mb-4">
          {gameOver ? (
            <p>Congratulations! You solved the puzzle in {userMoves} moves with {accuracy}% accuracy.</p>
          ) : suggestedMove ? (
            <p>
              Suggested move: Tower {suggestedMove[0] + 1} to Tower {suggestedMove[1] + 1}
            </p>
          ) : (
            <p>No valid moves available. Try moving a disk to progress.</p>
          )}
        </div>
        <div className="text-lg mb-4">Accuracy: {accuracy}%</div>
        <div className="text-lg mb-4">Moves: {userMoves} / {optimalMoves.length} (optimal)</div>
        <div className="space-x-4">
          <Button onClick={initializeGame}>Reset Game</Button>
        </div>
      </div>
    </DndProvider>
  )
}
