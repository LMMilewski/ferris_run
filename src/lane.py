import car, traffic_light, const

class Lane:
    
    def __init__(self, maxVelocity, trafficLights, direction, numberOfCars, pos, crossings, cfg):        
        self.maxVelocity = maxVelocity
        self.trafficLights = trafficLights
        self.direction = direction
        self.numberOfCars = numberOfCars
        self.pos = pos
        
        self.cars = [car.Car(self.maxVelocity, self.direction, cfg) for i in range(0, numberOfCars)]        
        x = pos[0]
        y = pos[1]               
        
        if direction == const.LEFT or direction == const.RIGHT:
            space = cfg.board_size[0]
            for r in crossings:
                space -= r[2]
        else:
            space = cfg.board_size[1]
            for r in crossings:
                space -= r[3]        
        
        
        offset = space / numberOfCars
        
        for i in range(0, numberOfCars):
            print x, y    
            for r in crossings:
                if x >= r[0] and x <= r[0] + r[2] and y >= r[1] and y <= r[1] + r[3]:
                    if direction == const.RIGHT:
                        x = r[0] + r[2]
                    elif direction == const.LEFT:
                        x = r[0] - self.cars[i].rect[2] 
                    elif direction == const.UP:
                        y = r[1] - self.cars[i].rect[3]
                    elif direction == const.DOWN:
                        y = r[1] + r[3] 
            self.cars[i].setCarAhead(self.cars[(i + 1) % self.numberOfCars])            
            self.cars[i].setPosition(x, y)
            x += offset * direction[0]
            y += offset * direction[1]
                    
        if self.trafficLights[0].getState() == traffic_light.RED:
            self.cars[0].stop(self.trafficLights[0])
        
    def changeState(self):
        for trafficLight in self.trafficLights:
            if trafficLight.getState() == traffic_light.YELLOW_BEFORE_GREEN or trafficLight.getState() == traffic_light.RED:
                return
            min = None
            if self.direction == const.RIGHT:
                for car in self.cars:
                    if car.getPosition()[0] + car.getSize()[0] < trafficLight.getPosition()[0] and (min == None or car.getPosition()[0] > min.getPosition()[0]):
                        min = car
            if self.direction == const.LEFT:
                for car in self.cars:
                    if car.getPosition()[0] > trafficLight.getPosition()[0] + trafficLight.getSize()[0] and (min == None or car.getPosition()[0] < min.getPosition()[0]):
                        min = car
            if self.direction == const.UP:
                for car in self.cars:
                    if car.getPosition()[1] > trafficLight.getPosition()[1] + trafficLight.getSize()[1] and (min == None or car.getPosition()[1] < min.getPosition()[1]):
                        min = car                    
                        
            if min == None:
                min = self.cars[-1]
            if trafficLight.getState() == traffic_light.YELLOW_BEFORE_RED:
                min.stop(trafficLight)
            elif trafficLight.getState() == traffic_light.GREEN:
                min.start()        
              
            
    def getCars(self):
        return self.cars
        