import kivy.context
import multiprocessing
import numpy as np
import pyautogui
from time import sleep
# import win32gui
from rx import interval, operators
from rx.scheduler import ThreadPoolScheduler
from src.gameplay.cavebot import resolveCavebotTasks, shouldAskForCavebotTasks
from src.gameplay.context import gameContext
from src.gameplay.combo import comboSpellsObserver
from src.gameplay.core.middlewares.battleList import setBattleListMiddleware
from src.gameplay.core.middlewares.chat import setChatTabsMiddleware
from src.gameplay.core.middlewares.gameWindow import setDirection, setHandleLoot, setGameWindowCreatures, setGameWindowMiddleware
from src.gameplay.core.middlewares.playerStatus import setMapPlayerStatusMiddleware
from src.gameplay.core.middlewares.radar import setRadarMiddleware, setWaypointIndex
from src.gameplay.core.middlewares.screenshot import setScreenshot
from src.gameplay.targeting import hasCreaturesToAttack
from src.gameplay.core.tasks.groupOfLootCorpse import GroupOfLootCorpseTasks
from src.gameplay.resolvers import resolveTasksByWaypoint
from src.gameplay.healing.observers.eatFood import eatFoodObserver
from src.gameplay.healing.observers.healingBySpells import healingBySpellsObserver
from src.gameplay.healing.observers.healingByPotions import healingByPotionsObserver
from src.gameplay.healing.observers.healingPriority import healingPriorityObserver
from src.repositories.gameWindow.creatures import getClosestCreature
from src.repositories.radar.core import getCoordinate
from src.repositories.radar.typings import Waypoint
from src.utils.core import getScreenshot, getScreenshot_osx
from src.ui.app import MyApp


OS = 'osx'
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


def main():
    optimalThreadCount = multiprocessing.cpu_count()
    threadPoolScheduler = ThreadPoolScheduler(optimalThreadCount)
    fpsCounter = 0.015625
    fpsObserver = interval(fpsCounter)
    
    def minimizeWindow(hwnd):
        win32gui.ShowWindow(hwnd, win32gui.SW_MINIMIZE)

    def maximizeWindow(hwnd):
        if OS == 'osx':
            hwnd.unhide()
        else:
            win32gui.ShowWindow(hwnd, 3)

    def focusWindow(hwnd):
        if OS == 'osx':
            hwnd.unhide()
        else:
            win32gui.SetForegroundWindow(hwnd)

    def handleGameData(_):
        global gameContext
        if gameContext['window'] is None:
            if OS == 'osx':
                from AppKit import NSWorkspace
                from AppKit import NSWorkspace, NSApplicationActivateIgnoringOtherApps
                #apps = NSWorkspace.sharedWorkspace().runningApplications()
                #gameContext['window'] = [ x for x in apps if x.localizedName() == 'Tibia'][0]
                #gameContext['window'].activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
            else:
                import win32gui
                gameContext['window'] = win32gui.FindWindow(None, 'Tibia - Lucas Monstro')
        if gameContext['pause']:
            return gameContext
        gameContext = setScreenshot(gameContext, is_osx=OS=='osx')
        gameContext = setRadarMiddleware(gameContext)
        gameContext = setChatTabsMiddleware(gameContext)
        gameContext = setBattleListMiddleware(gameContext)
        gameContext = setGameWindowMiddleware(gameContext)
        gameContext = setDirection(gameContext)
        gameContext = setGameWindowCreatures(gameContext)
        gameContext = setHandleLoot(gameContext)
        gameContext = setWaypointIndex(gameContext)
        gameContext = setMapPlayerStatusMiddleware(gameContext)
        return gameContext

    gameObserver = fpsObserver.pipe(
        operators.map(handleGameData),
        operators.filter(lambda ctx: ctx['pause'] == False),
    )

    def handleGameplayTasks(context):
        global gameContext
        gameContext = context
        hasCurrentTask = gameContext['currentTask'] is not None
        if hasCurrentTask and gameContext['currentTask'].name != 'lureCreatures' and (gameContext['currentTask'].status == 'completed' or len(gameContext['currentTask'].tasks) == 0):
            gameContext['currentTask'] = None
        if gameContext['currentTask'] is not None and gameContext['currentTask'].name == 'groupOfSelectLootTab':
            return gameContext
        hasCorpsesToLoot = len(gameContext['loot']['corpsesToLoot']) > 0
        if hasCorpsesToLoot:
            gameContext['way'] = 'lootCorpses'
            if gameContext['currentTask'] is not None and gameContext['currentTask'].name != 'groupOfLootCorpse':
                gameContext['currentTask'] = None
            if gameContext['currentTask'] is None:
                hasKeyPressed = gameContext['lastPressedKey'] is not None
                if hasKeyPressed:
                    pyautogui.keyUp(gameContext['lastPressedKey'])
                    gameContext['lastPressedKey'] = None
                # TODO: get closest dead corpse
                firstDeadCorpse = gameContext['loot']['corpsesToLoot'][0]
                gameContext['currentTask'] = GroupOfLootCorpseTasks(context, firstDeadCorpse)
            gameContext['gameWindow']['previousMonsters'] = gameContext['gameWindow']['monsters']
            return gameContext
        elif gameContext['currentTask'] is not None and gameContext['currentTask'].name == 'lureCreatures':
            gameContext['way'] = 'waypoint'
        elif hasCreaturesToAttack(context):
            targetCreature = getClosestCreature(gameContext['gameWindow']['creatures'], gameContext['radar']['coordinate'])
            hasTargetCreature = targetCreature != None
            if hasTargetCreature:
                gameContext['way'] = 'cavebot'
            else:
                gameContext['way'] = 'waypoint'
        else:
            gameContext['way'] = 'waypoint'
        if hasCreaturesToAttack(context) and shouldAskForCavebotTasks(gameContext):
            hasCurrentTaskAfterCheck = gameContext['currentTask'] is not None
            isTryingToAttackClosestCreature = hasCurrentTaskAfterCheck and (gameContext['currentTask'].name == 'groupOfAttackClosestCreature' or gameContext['currentTask'].name == 'groupOfFollowTargetCreature')
            isNotTryingToAttackClosestCreature = not isTryingToAttackClosestCreature
            if isNotTryingToAttackClosestCreature:
                newCurrentTask = resolveCavebotTasks(context)
                hasCurrentTask2 = gameContext['currentTask'] is not None
                if hasCurrentTask2:
                    hasTargetCreature = gameContext['cavebot']['targetCreature'] is not None or gameContext['cavebot']['closestCreature'] is not None
                    if hasTargetCreature:
                        hasKeyPressed = gameContext['lastPressedKey'] is not None
                        if hasKeyPressed:
                            pyautogui.keyUp(gameContext['lastPressedKey'])
                            gameContext['lastPressedKey'] = None
                        gameContext['currentTask'] = newCurrentTask
                else:
                    hasNewCurrentTask = newCurrentTask is not None
                    if hasNewCurrentTask:
                        hasKeyPressed = gameContext['lastPressedKey'] is not None
                        if hasKeyPressed:
                            pyautogui.keyUp(gameContext['lastPressedKey'])
                            gameContext['lastPressedKey'] = None
                        gameContext['currentTask'] = newCurrentTask
        elif gameContext['way'] == 'waypoint':
            if gameContext['currentTask'] == None:
                currentWaypointIndex = gameContext['cavebot']['waypoints']['currentIndex']
                currentWaypoint = gameContext['cavebot']['waypoints']['points'][currentWaypointIndex]
                gameContext['currentTask'] = resolveTasksByWaypoint(context, currentWaypoint)
        gameContext['gameWindow']['previousMonsters'] = gameContext['gameWindow']['monsters']
        return gameContext

    gameplayObservable = gameObserver.pipe(
        operators.filter(lambda ctx: ctx['pause'] == False),
        operators.map(handleGameplayTasks),
        operators.subscribe_on(threadPoolScheduler),
    )

    def gameplayObserver(context):
        global gameContext
        if gameContext['pause']:
            return
        if gameContext['currentTask'] is not None:
            gameContext = gameContext['currentTask'].do(context)
        gameContext['radar']['lastCoordinateVisited'] = gameContext['radar']['coordinate']

    def continueWhenIsNotChatTask(context):
        if context['currentTask'] is None:
            return
        chatTask = ['depositGold', 'groupOfRefill']
        return context['currentTask'].name not in chatTask

    eatFoodObservable = gameObserver.pipe(
        operators.filter(continueWhenIsNotChatTask),
        operators.subscribe_on(threadPoolScheduler)
    )
    healingPriorityObservable = gameObserver.pipe(
        operators.filter(continueWhenIsNotChatTask),
        operators.subscribe_on(threadPoolScheduler)
    )
    healingByPotionsObservable = gameObserver.pipe(
        operators.filter(continueWhenIsNotChatTask),
        operators.subscribe_on(threadPoolScheduler)
    )
    healingBySpellsObservable = gameObserver.pipe(
        operators.filter(continueWhenIsNotChatTask),
        operators.subscribe_on(threadPoolScheduler)
    )
    comboSpellsObservable = gameObserver.pipe(
        operators.filter(continueWhenIsNotChatTask),
        operators.subscribe_on(threadPoolScheduler)
    )

    class GameContext:
        def addWaypoint(self, waypoint):
            global gameContext
            gameContext['cavebot']['waypoints']['points'] = np.append(gameContext['cavebot']['waypoints']['points'], np.array([waypoint], dtype=Waypoint))

        def focusInTibia(self):
            global gameContext
            maximizeWindow(gameContext['window'])
            focusWindow(gameContext['window'])

        def play(self):
            #self.focusInTibia()
            sleep(1)
            gameContext['pause'] = False

        def pause(self):
            gameContext['pause'] = True
            gameContext['currentTask'] = None
            if gameContext['lastPressedKey'] is not None:
                pyautogui.keyUp(gameContext['lastPressedKey'])
                gameContext['lastPressedKey'] = None

        def getCoordinate(self):
            global gameContext
            screenshot = getScreenshot()
            
            coordinate = getCoordinate(screenshot, previousCoordinate=gameContext['radar']['previousCoordinate'])
            return coordinate

        def toggleHealingPotionsByKey(self, healthPotionType, enabled):
            global gameContext
            gameContext['healing']['potions'][healthPotionType]['enabled'] = enabled

        def setHealthPotionHotkeyByKey(self, healthPotionType, hotkey):
            global gameContext
            gameContext['healing']['potions'][healthPotionType]['hotkey'] = hotkey

        def setHealthPotionHpPercentageLessThanOrEqual(self, healthPotionType, hpPercentage):
            global gameContext
            gameContext['healing']['potions'][healthPotionType]['hpPercentageLessThanOrEqual'] = hpPercentage

        def toggleManaPotionsByKey(self, manaPotionType, enabled):
            global gameContext
            gameContext['healing']['potions'][manaPotionType]['enabled'] = enabled

        def setManaPotionManaPercentageLessThanOrEqual(self, manaPotionType, manaPercentage):
            global gameContext
            gameContext['healing']['potions'][manaPotionType]['manaPercentageLessThanOrEqual'] = manaPercentage

        def toggleHealingSpellsByKey(self, contextKey, enabled):
            global gameContext
            gameContext['healing']['spells'][contextKey]['enabled'] = enabled

        def setHealingSpellsHpPercentage(self, contextKey, hpPercentage):
            global gameContext
            gameContext['healing']['spells'][contextKey]['hpPercentageLessThanOrEqual'] = hpPercentage

        def setHealingSpellsHotkey(self, contextKey, hotkey):
            global gameContext
            gameContext['healing']['spells'][contextKey]['hotkey'] = hotkey

    try:
        eatFoodObservable.subscribe(eatFoodObserver)
        healingPriorityObservable.subscribe(healingPriorityObserver)
        healingByPotionsObservable.subscribe(healingByPotionsObserver)
        healingBySpellsObservable.subscribe(healingBySpellsObserver)
        comboSpellsObservable.subscribe(comboSpellsObserver)
        gameplayObservable.subscribe(gameplayObserver)
        kivy.context.register_context('game', GameContext)
        MyApp().run()
    except KeyboardInterrupt:
        raise SystemExit


if __name__ == '__main__':
    main()