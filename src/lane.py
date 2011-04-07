import car, traffic_light, const

class Lane:
    
    def __init__(self, maxVelocity, trafficLights, direction, numberOfCars, pos, crossings, cfg, res):        
        self.maxVelocity = maxVelocity
        self.trafficLights = trafficLights
        self.direction = direction
        self.numberOfCars = numberOfCars
        self.pos = pos
        
        if direction == const.LEFT or direction == const.RIGHT:
            space = cfg.board_size[0]  
            for r in crossings:
                space -= r[2]
        else:
            space = cfg.board_size[1]
            for r in crossings:
                space -= r[3]        
        
        
        car_distance = cfg.board_size[0] / numberOfCars
            
        
        self.cars = [car.Car(self.maxVelocity, self.direction, car_distance, cfg, res) for i in range(0, numberOfCars)]        
        x = pos[0]
        y = pos[1]               
        
        offset = space / numberOfCars
        
        for i in range(0, numberOfCars):
            for r in crossings:
                if x >= r[0] and x <= r[0] + r[2] and y >= r[1] and y <= r[1] + r[3]:
                    if direction == const.RIGHT:
                        x = r[0] + r[2]
                    elif direction == const.LEFT:
                        x = r[0] - self.cars[i].getSize()[1]
                    elif direction == const.UP:
                        y = r[1] - self.cars[i].getSize()[1]
                    elif direction == const.DOWN:
                        y = r[1] + r[3] 
            self.cars[i].setCarAhead(self.cars[(i + 1) % self.numberOfCars])            
            self.cars[i].setPosition(x, y)
            x += offset * direction[0]
            y += offset * direction[1]
        
        self.changeState()
                         
        
    def changeState(self):
        for trafficLight in self.trafficLights:
            if trafficLight.getState() == traffic_light.YELLOW_BEFORE_GREEN or trafficLight.getState() == traffic_light.RED:
                return
            min = self.cars[-1]
            for car in self.cars:
                if car.getDistance(trafficLight) < min.getDistance(trafficLight):
                    min = car
                                  
            if trafficLight.getState() == traffic_light.YELLOW_BEFORE_RED:
                min.stop(trafficLight)
            elif trafficLight.getState() == traffic_light.GREEN:
                min.start()        
              
            
    def getCars(self):
        return self.cars
        